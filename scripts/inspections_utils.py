# ruff: noqa: E501

import pandas as pd
import re
from openai import OpenAI
import duckdb
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from django.contrib.gis.geos import Point
from apt_app.models import Violation

load_dotenv()

# ----- PREPROCESSING AND PROMPT GENERATION -----

HP_NORTH_BOUND = 41.809647
HP_SOUTH_BOUND = 41.780482
HP_WEST_BOUND = -87.615877
HP_EAST_BOUND = -87.579056

ADDRESSES_TO_CHECK = [
    "5220 S HARPER AVE",
    "5514 S BLACKSTONE AVE",
    "5132 S CORNELL AVE",
    "5801 S DORCHESTER AVE",
    "1001 E 53RD ST",  # should have no non-trivial violations -- needs to be skipped and should have no summary
]

TRIVIAL_VIOLATION_CODES_DF = pd.DataFrame(
    [
        ["CN190019", "ARRANGE PREMISE INSPECTION", "inspector having no entry"],
        ["CN193305", "ARRANGE PREMISE INSPECTION", "inspector having no entry"],
        ["CN190029", "ARRANGE FOR REINSPECTION REGAR", "inspector having no entry"],
    ],
    columns=["code", "description", "summary"],
)

TRIVIAL_VIOLATION_CODES = TRIVIAL_VIOLATION_CODES_DF["code"].tolist()

BASE_PROMPT = """
Your goal is to summarize lengthy inspection records for an apartment building into a succinct, \
reader-friendly format that is digestible and informative for a tenant searching for an apartment. \
You will be provided a concatenated report of alleged violations, and should output a json \
object like the following:

{
  "summary": "This building was cited <'recently' or specify when> for alleged violations around <...> and <...> concerns,
  including <one predominant issue such as 'inadequate heating in at least one unit'> and
  <one or two other issues>."

  "summarized_issues": [
    {
      "date": "Jan 04, 2025", // following the Mon DD, YYYY format
      "issues": [
        {
          "emoji": "🧊", // use a relevant emoji and if possible a different one for each issue
          "description": "Insufficient heating (60°F in living room and kitchen) and low hot water pressure in Unit <a, b, c>." //
        },
      ]
    },'
    {
      "date": "Mar 15, 2024",
      "issues": [
        {
          "emoji": "🎨",
          "description": "Graffiti and overflowing trash in rear of building"
        },
      ]
    }
  ]
}

The key is for each summarized issue description to be a concise and meaningful reorganization of \
otherwise too detailed or esoteric alleged violations. Depending on thematic relevance and violation \
location, multiple violations may be grouped into a single issue -- or one violation may be split \
into multiple issues. When available, also specify the unit number or building area in parentheses \
at the end of the description. The original full-length concatenated report is as follows: \
"""

# omitted part of the prompt:
"""
In the summary, please omit any inspection records on the following issues:
- unauthorized use of space as an event venue
- inspector denied entry or need for re-inspecton in the records
- any other issues that do not impact quality of life and likely not of interest to future tenants
"""


def filter_by_violation_code(code: str, df: pd.DataFrame) -> pd.DataFrame:
    return df[df["VIOLATION CODE"] == code]


def print_df_stats(func):
    def wrapper(df_in: pd.DataFrame, *args, **kwargs):
        df_out: pd.DataFrame = func(df_in, *args, **kwargs)
        print(f"There are {len(df_out)} rows, with {df_out['ADDRESS'].nunique()} unique addresses")
        return df_out

    return wrapper


@print_df_stats
def filter_and_recast_columns(df: pd.DataFrame) -> pd.DataFrame:
    query = """
    SELECT
        ADDRESS
        ,"ID" as "VIOLATION ID"
        ,strptime("VIOLATION DATE", '%m/%d/%Y') as "VIOLATION DATE"
        ,"DEPARTMENT BUREAU"
        ,"INSPECTION NUMBER" as "INSPECTION ID"
        ,"INSPECTION CATEGORY"
        ,"INSPECTION STATUS"
        , "INSPECTOR ID"
        ,"VIOLATION ORDINANCE"
        ,"VIOLATION CODE"
        ,"VIOLATION DESCRIPTION"
        ,"VIOLATION LOCATION"
        ,"VIOLATION INSPECTOR COMMENTS"
        ,"VIOLATION STATUS"
        , "VIOLATION STATUS DATE"
    FROM df
    ORDER BY ADDRESS, "VIOLATION DATE" desc, "INSPECTION CATEGORY"
    """
    return duckdb.sql(query).df()


@print_df_stats
def filter_by_date(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    query = f"""
    SELECT *
    FROM df
    WHERE "VIOLATION DATE" BETWEEN '{start_date}' AND '{end_date}'
    """
    return duckdb.sql(query).df()


@print_df_stats
def filter_for_recent(df: pd.DataFrame, start_date: str = "2020-01-01") -> pd.DataFrame:
    query = f"""
    SELECT *
    FROM df
    WHERE "VIOLATION DATE" >= DATE '{start_date}'
    """
    return duckdb.sql(query).df()


@print_df_stats
def filter_for_hyde_park(df: pd.DataFrame) -> pd.DataFrame:
    query = f"""
    SELECT *
    FROM df
    WHERE LATITUDE BETWEEN {HP_SOUTH_BOUND} AND {HP_NORTH_BOUND}
        AND LONGITUDE BETWEEN {HP_WEST_BOUND} AND {HP_EAST_BOUND}
    """
    return duckdb.sql(query).df()


@print_df_stats
def filter_by_inspection_categories(df: pd.DataFrame, categories: list[str]) -> pd.DataFrame:
    categories_upper = [c.upper() for c in categories]
    return df[df["INSPECTION CATEGORY"].isin(categories_upper)]


def remove_trivial_violations_by_code(
    df: pd.DataFrame, trivial_codes: list[str] = TRIVIAL_VIOLATION_CODES
) -> pd.DataFrame:
    return df[~df["VIOLATION CODE"].isin(trivial_codes)]


def generate_summary_of_trivial_violations(df: pd.DataFrame, trivial_codes: list):
    """
    Fetch violation records that are considered trivial by violation code and summarize the issues
    into a one-liner like "Unauthorized uses and cases where inspectors were denied entry were omitted."

    # NOTE: might need to change arg from df to address
    """
    # find trivial violations by 'Violation Code'
    # trivial_violations = df.loc[df["VIOLATION CODE"].isin(trivial_codes), "VIOLATION CODE"]
    # TODO
    return


def filter_df_by_address(address: str, df: pd.DataFrame) -> pd.DataFrame:
    return df[df["ADDRESS"].str.upper().str.startswith(address.upper())]


_TRAILING_CODES = re.compile(
    r"""\s*              # the blank(s) just before the codes
        \(               # opening parenthesis that begins the codes
        [^()]*           # anything that is not another parenthesis
        (?:              # …optionally, one-level nested (…) like “(b)”
            \([^()]*\)   #   the inner pair
            [^()]*       #   stuff after the inner pair
        )*               #   …repeat as needed
        \)?              # optional closing “)” (covers malformed strings)
        \s*$             # only whitespace until end-of-line
    """,
    re.VERBOSE,
)


def remove_trailing_code_citation(text: str) -> str:
    """
    Strip the trailing Chicago-style building-code parentheses, if present.
    """
    if not text:
        return ""
    return _TRAILING_CODES.sub("", text).rstrip()


def generate_concat_report_for_one_occasion(df: pd.DataFrame) -> str:
    """
    Helper function to generate the concatenated report for a single inspection occasion (defined by a
    unique date).

    The concatenated report should look like:
    On <date>, this property was cited for <n> alleged violations:
    - 1) it allegedly violated city ordiance <>; inspector commented: <>;
    - 2) it allegedly violated city ordiance <>; inspector commented: <>;
    - ...
    """
    df.reset_index(drop=True, inplace=True)
    total_violations_count = len(df)
    occasion_date = df["VIOLATION DATE"].iloc[0].strftime("%Y-%m-%d")
    r = f"On {occasion_date}, it was cited for the following {total_violations_count} violations: "

    for i, row in df.iterrows():
        violation_ordinance = row["VIOLATION ORDINANCE"]
        cleaned_violation_ordinance = remove_trailing_code_citation(violation_ordinance)
        inspector_comments = row["VIOLATION INSPECTOR COMMENTS"]
        r += f"{i + 1}) Inspector noted issue(s) with '{inspector_comments}' -- which allegedly violated city ordiance '{cleaned_violation_ordinance}'; "

    return r


def generate_concat_report_for_all_occasions(df: pd.DataFrame) -> str:
    """
    Concatenate the concatenated reports from all inspection occasions for a given address.
    """
    df = df.sort_values(by=["VIOLATION DATE", "INSPECTION ID"], ascending=False)
    unique_occasion_dates = df["VIOLATION DATE"].unique()
    out = "This building was cited on the following occasions: "
    for occasion_date in unique_occasion_dates:
        df_occasion = df[df["VIOLATION DATE"] == occasion_date]
        out += "\n\n" + generate_concat_report_for_one_occasion(df_occasion)
    return out


def generate_prompt_from_address(address, df, base_prompt=BASE_PROMPT):
    # find the subset of df that matches the address
    df = filter_df_by_address(address, df)
    # remove trivial violations
    df = remove_trivial_violations_by_code(df, trivial_codes=TRIVIAL_VIOLATION_CODES)
    # generate concatenated report
    concat_report = generate_concat_report_for_all_occasions(df)
    # generate prompt
    prompt = base_prompt + "\n" + concat_report
    return prompt


def clean_json_string(json_string: str) -> str:
    """
    If the string is fenced in a Markdown ```json … ``` code block,
    return only the JSON inside.  Otherwise return the original string,
    trimmed of leading/trailing whitespace.
    """
    # Look for the *first* ```json … ``` block, ignoring anything after it.
    pattern = r"```json\s*(.*?)\s*```"
    m = re.search(pattern, json_string, flags=re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else json_string.strip()


# ----- LLM API CALLS -----
DS_PROVER_V2 = "deepseek/deepseek-prover-v2:free"
GPT_41 = "openai/gpt-4.1"
GEMINI_25 = "google/gemini-2.5-flash-preview-05-20"

MODELS = [DS_PROVER_V2, GPT_41]

OPENROUTER_CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def query_request_mapper(address: str, df: pd.DataFrame) -> dict:
    return {
        DS_PROVER_V2: {
            "model": DS_PROVER_V2,
            "response_format": {"type": "json_schema"},
            "messages": [
                {
                    "role": "user",
                    "content": generate_prompt_from_address(
                        address, df=df, base_prompt=BASE_PROMPT
                    ),
                },
            ],
        },
        GPT_41: {
            "model": GPT_41,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": generate_prompt_from_address(
                                address, df=df, base_prompt=BASE_PROMPT
                            ),
                        }
                    ],
                }
            ],
        },
        GEMINI_25: {
            "model": GEMINI_25,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": generate_prompt_from_address(
                                address, df=df, base_prompt=BASE_PROMPT
                            ),
                        }
                    ],
                }
            ],
        },
    }


def llm_summarize_for_one_address(
    address: str, df: pd.DataFrame, model: str, client: OpenAI = OPENROUTER_CLIENT
) -> dict:
    completion = client.chat.completions.create(**query_request_mapper(address, df)[model])
    # raw_return still may contain markdown markers i.e. ```json
    try:
        raw_return = completion.choices[0].message.content
        parsed_return = json.loads(clean_json_string(raw_return))
        return parsed_return
    except Exception as e:
        print(f"Error {e} in parsing {raw_return}")
        return {}


def generate_summary_for_one_address(address, df, model):
    print(f"ADDRESS: {address}")
    # first check if the address has any non-trivial violations
    # by checking if the df is empty if trivial violations are removed
    df_filtered = filter_df_by_address(address, df).pipe(remove_trivial_violations_by_code)
    if df_filtered.empty:
        print("No non-trivial violations, skipping...\n----------------------------")
        return None
    # if df_filtered is not empty, summarize
    summary_json = llm_summarize_for_one_address(address=address, df=df, model=model)
    print(f"SUMMARY: {summary_json}")
    print("\n----------------------------")
    return summary_json


# ----- DATA INGESTION -----


def convert_date(
    date_str: str, input_format: str = "%m/%d/%Y", output_format: str = "%Y-%m-%d"
) -> str | None:
    """
    Convert a date string from one format to another.

    :param date_str: The date string to convert.
    :param input_format: The format of the input date string.
    :param output_format: The desired format for the output date string.
    :return: The converted date string.
    """
    if isinstance(date_str, float):
        return None
    # Check for empty or whitespace-only strings
    if not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str, input_format).strftime(output_format)
    except ValueError as e:
        raise ValueError(f"Error converting date: {e}")


def create_one_violation_object(row) -> Violation:
    return Violation(
        violation_id=row["ID"],
        violation_last_modified_date=convert_date(row["VIOLATION LAST MODIFIED DATE"]),
        violation_date=convert_date(row["VIOLATION DATE"]),
        violation_code=row["VIOLATION CODE"],
        violation_status=row["VIOLATION STATUS"],
        violation_status_date=convert_date(row["VIOLATION STATUS DATE"]),
        violation_description=row["VIOLATION DESCRIPTION"],
        violation_location=row["VIOLATION LOCATION"],
        violation_inspector_comments=row["VIOLATION INSPECTOR COMMENTS"],
        violation_ordinance=row["VIOLATION ORDINANCE"],
        inspector_id=row["INSPECTOR ID"],
        inspection_number=row["INSPECTION NUMBER"],
        inspection_status=row["INSPECTION STATUS"],
        inspection_waived=row["INSPECTION WAIVED"],
        inspection_category=row["INSPECTION CATEGORY"],
        department_bureau=row["DEPARTMENT BUREAU"],
        address=row["ADDRESS"],
        street_number=row["STREET NUMBER"],
        street_direction=row["STREET DIRECTION"],
        street_name=row["STREET NAME"],
        street_type=row["STREET TYPE"],
        property_group=row["PROPERTY GROUP"],
        ssa=row["SSA"],
        latitude=row["LATITUDE"],
        longitude=row["LONGITUDE"],
        location=Point(float(row["LATITUDE"]), float(row["LONGITUDE"])),  # FIXME
    )
