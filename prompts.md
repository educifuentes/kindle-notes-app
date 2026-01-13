
refactor based on @Analyzing Kindle Highlights 

The output of the final function is a pandas dataframe

pandas dataframe columns:
   ["location", "page", "section", "sub_section", "highlighted_text", "note",  "is_very_important", "is_important"]


columns rules

highlighted_text: is the text of the highlight
note: is the text of the user
is_very_important: if note starts with "wow iii" (case insensitive)
is_important: if note starts with "wow" (case insensitive)


