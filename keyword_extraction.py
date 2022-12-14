from keybert import KeyBERT
import yake
""""""
text1 = ["Credit card skimmer found at 7-Eleven in York County - WGAL Susquehanna Valley Pa",
         "GameStop Chairman Ryan Cohen and CEO Matt Furlong promised to turn the gaming retailer into one of operational excellence and amazing store experiences while cashing in on new opportunities like cryp",
         "eline Dion has been diagnosed with Stiff Person Syndrome (SPS), which causes her muscles to tense uncontrollably. The condition ultimately leaves sufferers as 'human statues' as it progressively"]

doc = """

This week offers multiple opportunities to get a great look at Mars thanks to several livestreams of Red Planet astronomical events.
Watch Mars be eclipsed by the moon tonight in free webcast - Space.com


"""
kw_model = KeyBERT()
keywords = kw_model.extract_keywords(doc)
print(keywords)

kw_extractor = yake.KeywordExtractor(top=5, n=2)

keywords = kw_extractor.extract_keywords(doc)
print(keywords)
