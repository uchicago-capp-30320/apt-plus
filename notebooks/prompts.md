Your goal is to extract movie categories from movie descriptions, as well as a 1-sentence summary for these movies.
You will be provided with a movie description, and you will output a json object containing the following information:

{
    categories: string[] // Array of categories based on the movie description,
    summary: string // 1-sentence summary of the movie based on the movie description
}

-----

Your goal is to summarize long inspection records for an apartment building into a succinct report with a one-line summary as well as bullet points of issues spotted on each occasion. You will be provided a concatenated string of the inspection records, and you will output a single json object that looks like the following example (you should NOT wrap the returned JSON object within any markdown markers such as ```json):

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
    },
    {
      "date": "Mar 2024",
      "issues": [
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

In the summary, please omit any inspection records on the following issues:
- unauthorized use of space as an event venue
- inspector denied entry or need for re-inspecton in the records
- any other issues that do not impact quality of life and likely not of interest to future tenants
