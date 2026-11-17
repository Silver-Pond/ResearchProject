THE LAST SIGNAL - RESEARCH FEATURES

INSTALLATION
1. Back up your existing project.
2. Replace main.py and station.py with the files in this package.
3. Add research.py to the same folder as main.py.
4. Keep eli_npc.py and sentiment_analyzer.py alongside them.
5. Run: python main.py

RESEARCH FLOW
- Select RESEARCH MODE.
- Read the research information screen and press ENTER.
- Each research session is randomly allocated to control or adaptive dialogue.
- Talk to E.L.I. at least once and inspect all three research terminals.
- The questionnaire appears after these tasks.
- LEFT/RIGHT selects a rating from 1 to 5; UP/DOWN changes question.
- Press ENTER on the final question to append the response to research_data.csv.

CSV CONTENTS
Anonymous session code, condition, UTC timestamp, completion flag, five questionnaire
ratings, conversation count and average emotion-classifier confidence. Raw typed messages,
participant names and chat transcripts are not exported. research_data.csv stores questionnaire/session summaries; research_interactions.csv stores per-message emotion labels and confidence values. Both are created beside main.py.

RESEARCH / ETHICS
The introductory screen is not a substitute for the approved information sheet and consent
process. Have the questionnaire and procedure reviewed and approved before collecting data.
Do not ask participants to type identifying information. Protect the CSV and follow the
approved retention and deletion plan. Random allocation is implemented, but allocation is
not block-balanced, so group sizes may differ. Normal START GAME play is not recorded.

COMPLETION
Research completion currently requires at least one E.L.I. message and all three terminals
to be read. Press E near E.L.I. or a terminal to interact.
