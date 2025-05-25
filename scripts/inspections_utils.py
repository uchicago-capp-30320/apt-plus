# ruff: noqa: E501

import pandas as pd

ADDRESSES_TO_CHECK = [
    "5220 S HARPER AVE",
    "5514 S BLACKSTONE AVE",
    "5132 S CORNELL AVE",
    "5801 S DORCHESTER AVE",
]


TRIVIAL_VIOLATION_CODES = [
    ["CN190019", "ARRANGE PREMISE INSPECTION", "inspector having no entry"],
    ["CN193305", "ARRANGE PREMISE INSPECTION", "inspector having no entry"],
]

BASE_PROMPT = """
You are a helpful assistant that summarizes long inspection records for an apartment building into a succinct report with a one-line summary as well as bullet points of issues spotted on each occasion. You will be provided a concatenated string of the inspection records, and you will output a single json object that looks like the following example: "

{
  "summary": "This building has received recent complaints regarding <> and <> concerns, including inadequate heat in at least one unit and multiple violations related to <>, which may pose potential <> risks",
  "note": "Some issues on <> are omitted for brevity."
  "summarized_issues": [
    {
      "date": "Jan 2025", // following the Mon YYYY format
      "issues": [
        {
          "emoji": "🧊", // use a relevant emoji and if possible a different one for each issue
          "description": "Insufficient heating (60°F in living room and kitchen) in Unit a, b, c" //
        },
        {
          "emoji": "🚿",
          "description": "Low hot water pressure and substandard temperature (as low as 45°F) in Units a, b, c"
        }
      ]
    },'
    {
      "date": "Mar 2024",
      "issues": []
        {
          "emoji": "🎨",
          "description": "Graffiti and overflowing trash in rear of building"
        },
        {
          "emoji": "🚪",
          "description": "Multiple apartment and hallway doors jammed, missing, or propped open with wedges—posing potential fire safety risks"
        }
      ]
    }
  ]
}

Use a more neural tone that resembles an inspector or assessor but is less esoteric and more appropriate -- one that is appropriate for presentation on an app that helps tenants find apartments. Each summarized issue description should be a short bullet-point summary that, when available, also specifies the unit number or building area at the end.

The original full-length narrative report to be summarized reads as follows:
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


def remove_trivial_violations_by_code(df: pd.DataFrame, trivial_codes: list) -> pd.DataFrame:
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


def generate_narrative_report_for_one_occasion(df: pd.DataFrame) -> str:
    """
    Helper function to generate the narrative report for a single inspection occasion (defined by a
    unique date).

    The narrative report should look like:
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
        inspector_comments = row["VIOLATION INSPECTOR COMMENTS"]
        r += f"{i + 1}) it allegedly violated city ordiance '{violation_ordinance}'. Inspector commented: '{inspector_comments}'; "

    return r


def generate_narrative_report_for_all_occasions(df: pd.DataFrame) -> str:
    """
    Concatenate the narrative reports from all inspection occasions for a given address.
    """
    df = df.sort_values(by=["VIOLATION DATE", "INSPECTION ID"], ascending=False)
    unique_occasion_dates = df["VIOLATION DATE"].unique()
    out = "This building was cited for the following violations: "
    for occasion_date in unique_occasion_dates:
        df_occasion = df[df["VIOLATION DATE"] == occasion_date]
        out += "\n\n" + generate_narrative_report_for_one_occasion(df_occasion)
    return out


def generate_prompt_from_address(address, df):
    # NOTE: WIP
    df = filter_df_by_address(address, df=df)

    df.sort_values(by=["VIOLATION DATE", ""], ascending=False)

    pass
