"""SRD background data for D&D 5e.

This module contains backgrounds from the System Reference Document (SRD).
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dnd_manager.data.feats import Feat


@dataclass
class BackgroundFeature:
    """A background feature."""
    name: str
    description: str


@dataclass
class Background:
    """A character background definition.

    Backgrounds can support multiple rulesets:
    - 2014 D&D: Uses feature (BackgroundFeature) for the special ability
    - 2024 D&D: Uses origin_feat and ability_score_options
    - ToV: Similar to 2014 with feature

    The ruleset field indicates which rules system the background was designed for:
    - None: Universal, works with any ruleset (has both 2014 and 2024 fields)
    - "dnd2014": Only for D&D 2014 rules
    - "dnd2024": Only for D&D 2024 rules
    - "tov": Only for Tales of the Valiant
    """
    name: str
    description: str
    skill_proficiencies: list[str]
    tool_proficiencies: list[str] = field(default_factory=list)
    languages: int = 0  # Number of language choices
    equipment: list[str] = field(default_factory=list)
    feature: Optional[BackgroundFeature] = None  # 2014/ToV feature
    # 2024 PHB additions
    ability_score_options: list[str] = field(default_factory=list)  # For 2024 rules
    origin_feat: Optional[str] = None  # For 2024 rules
    # Ruleset support
    ruleset: Optional[str] = None  # None = universal, "dnd2014", "dnd2024", "tov"


# SRD Backgrounds
ACOLYTE = Background(
    name="Acolyte",
    description="You have spent your life in the service of a temple to a specific god or pantheon of gods.",
    skill_proficiencies=["Insight", "Religion"],
    languages=2,
    equipment=["Holy symbol", "Prayer book or prayer wheel", "5 sticks of incense",
               "Vestments", "Common clothes", "15 gp"],
    feature=BackgroundFeature(
        "Shelter of the Faithful",
        "You and your adventuring companions can expect free healing at temples of your faith. You can find a place to hide, rest, or recuperate among believers."
    ),
    ability_score_options=["Intelligence", "Wisdom", "Charisma"],
    origin_feat="Magic Initiate (Cleric)",
)

CHARLATAN = Background(
    name="Charlatan",
    description="You have always had a way with people. You know what makes them tick, you can tease out their hearts' desires, and with a few leading questions you can read them like they were children's books.",
    skill_proficiencies=["Deception", "Sleight of Hand"],
    tool_proficiencies=["Disguise kit", "Forgery kit"],
    equipment=["Fine clothes", "Disguise kit", "Tools of the con of your choice", "15 gp"],
    feature=BackgroundFeature(
        "False Identity",
        "You have created a second identity that includes documentation, established acquaintances, and disguises that allow you to assume that persona."
    ),
    ability_score_options=["Dexterity", "Constitution", "Charisma"],
    origin_feat="Skilled",
)

CRIMINAL = Background(
    name="Criminal",
    description="You are an experienced criminal with a history of breaking the law. You have spent a lot of time among other criminals and still have contacts within the criminal underworld.",
    skill_proficiencies=["Deception", "Stealth"],
    tool_proficiencies=["One type of gaming set", "Thieves' tools"],
    equipment=["Crowbar", "Dark common clothes with hood", "15 gp"],
    feature=BackgroundFeature(
        "Criminal Contact",
        "You have a reliable and trustworthy contact who acts as your liaison to a network of other criminals."
    ),
    ability_score_options=["Dexterity", "Constitution", "Intelligence"],
    origin_feat="Alert",
)

ENTERTAINER = Background(
    name="Entertainer",
    description="You thrive in front of an audience. You know how to entrance them, entertain them, and even inspire them.",
    skill_proficiencies=["Acrobatics", "Performance"],
    tool_proficiencies=["Disguise kit", "One type of musical instrument"],
    equipment=["Musical instrument of your choice", "The favor of an admirer",
               "Costume", "15 gp"],
    feature=BackgroundFeature(
        "By Popular Demand",
        "You can always find a place to perform in any settlement. You receive free lodging and food in exchange for performing each night."
    ),
    ability_score_options=["Strength", "Dexterity", "Charisma"],
    origin_feat="Musician",
)

FOLK_HERO = Background(
    name="Folk Hero",
    description="You come from a humble social rank, but you are destined for so much more. The people of your home village regard you as their champion.",
    skill_proficiencies=["Animal Handling", "Survival"],
    tool_proficiencies=["One type of artisan's tools", "Vehicles (land)"],
    equipment=["Artisan's tools of your choice", "Shovel", "Iron pot",
               "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Rustic Hospitality",
        "Since you come from the ranks of the common folk, you can fit in among them with ease. You can find a place to hide, rest, or recuperate among commoners."
    ),
    ability_score_options=["Strength", "Constitution", "Wisdom"],
    origin_feat="Tough",
)

GUILD_ARTISAN = Background(
    name="Guild Artisan",
    description="You are a member of an artisan's guild, skilled in a particular field and closely associated with other artisans.",
    skill_proficiencies=["Insight", "Persuasion"],
    tool_proficiencies=["One type of artisan's tools"],
    languages=1,
    equipment=["Artisan's tools of your choice", "Letter of introduction from your guild",
               "Traveler's clothes", "15 gp"],
    feature=BackgroundFeature(
        "Guild Membership",
        "As an established and respected member of a guild, you can rely on certain benefits that membership provides."
    ),
    ability_score_options=["Strength", "Dexterity", "Intelligence"],
    origin_feat="Crafter",
)

HERMIT = Background(
    name="Hermit",
    description="You lived in seclusion – either in a sheltered community such as a monastery, or entirely alone – for a formative part of your life.",
    skill_proficiencies=["Medicine", "Religion"],
    tool_proficiencies=["Herbalism kit"],
    languages=1,
    equipment=["Scroll case stuffed with notes from your studies", "Winter blanket",
               "Common clothes", "Herbalism kit", "5 gp"],
    feature=BackgroundFeature(
        "Discovery",
        "The quiet seclusion of your extended hermitage gave you access to a unique and powerful discovery."
    ),
    ability_score_options=["Constitution", "Wisdom", "Charisma"],
    origin_feat="Healer",
)

NOBLE = Background(
    name="Noble",
    description="You understand wealth, power, and privilege. You carry a noble title, and your family owns land, collects taxes, and wields significant political influence.",
    skill_proficiencies=["History", "Persuasion"],
    tool_proficiencies=["One type of gaming set"],
    languages=1,
    equipment=["Fine clothes", "Signet ring", "Scroll of pedigree", "25 gp"],
    feature=BackgroundFeature(
        "Position of Privilege",
        "Thanks to your noble birth, people are inclined to think the best of you. You are welcome in high society, and people assume you have the right to be wherever you are."
    ),
    ability_score_options=["Strength", "Constitution", "Charisma"],
    origin_feat="Skilled",
)

OUTLANDER = Background(
    name="Outlander",
    description="You grew up in the wilds, far from civilization and the comforts of town and technology.",
    skill_proficiencies=["Athletics", "Survival"],
    tool_proficiencies=["One type of musical instrument"],
    languages=1,
    equipment=["Staff", "Hunting trap", "Trophy from an animal you killed",
               "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Wanderer",
        "You have an excellent memory for maps and geography, and you can always recall the general layout of terrain. You can also find food and fresh water for yourself and up to five other people each day."
    ),
    ability_score_options=["Strength", "Dexterity", "Wisdom"],
    origin_feat="Tough",
)

SAGE = Background(
    name="Sage",
    description="You spent years learning the lore of the multiverse. You scoured manuscripts, studied scrolls, and listened to the greatest experts on the subjects that interest you.",
    skill_proficiencies=["Arcana", "History"],
    languages=2,
    equipment=["Bottle of black ink", "Quill", "Small knife",
               "Letter from a dead colleague with a question you haven't been able to answer",
               "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Researcher",
        "When you attempt to learn or recall a piece of lore, if you do not know that information, you often know where and from whom you can obtain it."
    ),
    ability_score_options=["Constitution", "Intelligence", "Wisdom"],
    origin_feat="Magic Initiate (Wizard)",
)

SAILOR = Background(
    name="Sailor",
    description="You sailed on a seagoing vessel for years. In that time, you faced down mighty storms, monsters of the deep, and those who wanted to sink your craft to the bottomless depths.",
    skill_proficiencies=["Athletics", "Perception"],
    tool_proficiencies=["Navigator's tools", "Vehicles (water)"],
    equipment=["Belaying pin (club)", "50 feet of silk rope", "Lucky charm",
               "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Ship's Passage",
        "When you need to, you can secure free passage on a sailing ship for yourself and your adventuring companions."
    ),
    ability_score_options=["Strength", "Dexterity", "Wisdom"],
    origin_feat="Tavern Brawler",
)

SOLDIER = Background(
    name="Soldier",
    description="War has been your life for as long as you care to remember. You trained as a youth, studied the use of weapons and armor, learned basic survival techniques.",
    skill_proficiencies=["Athletics", "Intimidation"],
    tool_proficiencies=["One type of gaming set", "Vehicles (land)"],
    equipment=["Insignia of rank", "Trophy taken from a fallen enemy",
               "Set of bone dice or deck of cards", "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Military Rank",
        "You have a military rank from your career as a soldier. Soldiers loyal to your former military organization still recognize your authority and influence."
    ),
    ability_score_options=["Strength", "Dexterity", "Constitution"],
    origin_feat="Savage Attacker",
)

URCHIN = Background(
    name="Urchin",
    description="You grew up on the streets alone, orphaned, and poor. You had no one to watch over you or to provide for you, so you learned to provide for yourself.",
    skill_proficiencies=["Sleight of Hand", "Stealth"],
    tool_proficiencies=["Disguise kit", "Thieves' tools"],
    equipment=["Small knife", "Map of the city you grew up in",
               "Pet mouse", "Token to remember your parents by", "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "City Secrets",
        "You know the secret patterns and flow to cities and can find passages through the urban sprawl that others would miss."
    ),
    ability_score_options=["Dexterity", "Wisdom", "Charisma"],
    origin_feat="Lucky",
)

# Additional Backgrounds (Original AI-generated descriptions)
FARMER = Background(
    name="Farmer",
    description="You spent years working the land, tending crops and livestock. The rhythms of planting and harvest shaped your life, teaching you patience and resilience.",
    skill_proficiencies=["Animal Handling", "Nature"],
    tool_proficiencies=["Carpenter's tools", "Vehicles (land)"],
    equipment=["Shovel", "Iron pot", "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Rustic Hospitality",
        "Common folk will offer you shelter and food when possible. Your humble demeanor puts rural people at ease."
    ),
    ability_score_options=["Strength", "Constitution", "Wisdom"],
    origin_feat="Tough",
)

GUARD = Background(
    name="Guard",
    description="You served as a guard protecting a settlement, caravan, or noble estate. Long hours of vigilance taught you to spot trouble before it arrives.",
    skill_proficiencies=["Athletics", "Perception"],
    tool_proficiencies=["One type of gaming set", "Vehicles (land)"],
    equipment=["Uniform", "Horn", "Manacles", "10 gp"],
    feature=BackgroundFeature(
        "Watcher's Eye",
        "Your experience spotting threats helps you find watch posts and understand guard rotations in unfamiliar places."
    ),
    ability_score_options=["Strength", "Dexterity", "Wisdom"],
    origin_feat="Alert",
)

MERCHANT = Background(
    name="Merchant",
    description="You made your living buying and selling goods, learning to appraise value and negotiate deals across diverse markets.",
    skill_proficiencies=["Insight", "Persuasion"],
    tool_proficiencies=["Navigator's tools"],
    languages=1,
    equipment=["Fine clothes", "Merchant's scale", "15 gp"],
    feature=BackgroundFeature(
        "Trade Contacts",
        "You know merchants and traders in major settlements who can help you find buyers, sellers, and market information."
    ),
    ability_score_options=["Constitution", "Intelligence", "Charisma"],
    origin_feat="Lucky",
)

SCRIBE = Background(
    name="Scribe",
    description="You devoted yourself to the written word, copying texts and recording knowledge. Your careful hand and sharp memory serve you well.",
    skill_proficiencies=["History", "Investigation"],
    tool_proficiencies=["Calligrapher's supplies"],
    languages=2,
    equipment=["Quill", "Ink", "Parchment sheets", "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Library Access",
        "You know how to navigate archives and gain access to libraries, scriptoriums, and collections of written knowledge."
    ),
    ability_score_options=["Intelligence", "Wisdom", "Charisma"],
    origin_feat="Skilled",
)

WAYFARER = Background(
    name="Wayfarer",
    description="You have spent your life on the road, traveling between settlements and rarely staying in one place for long. The open road is your true home.",
    skill_proficiencies=["Insight", "Survival"],
    tool_proficiencies=["Thieves' tools"],
    languages=1,
    equipment=["Traveler's clothes", "Bedroll", "Walking stick", "15 gp"],
    feature=BackgroundFeature(
        "Wanderer's Intuition",
        "You have a knack for finding safe places to rest and can sense when an area is dangerous or welcoming to travelers."
    ),
    ability_score_options=["Dexterity", "Wisdom", "Charisma"],
    origin_feat="Lucky",
)

ARTISAN = Background(
    name="Artisan",
    description="You learned a craft and take pride in creating things with your hands. Whether smith, carpenter, or weaver, your skills are valued.",
    skill_proficiencies=["Investigation", "Persuasion"],
    tool_proficiencies=["One type of artisan's tools"],
    languages=1,
    equipment=["Artisan's tools", "Guild letter", "Traveler's clothes", "15 gp"],
    feature=BackgroundFeature(
        "Maker's Mark",
        "Fellow craftspeople recognize quality work and are inclined to offer you professional courtesy and fair deals."
    ),
    ability_score_options=["Strength", "Dexterity", "Intelligence"],
    origin_feat="Crafter",
)

PILGRIM = Background(
    name="Pilgrim",
    description="You journeyed to sacred sites seeking spiritual fulfillment. The hardships of the road strengthened both body and faith.",
    skill_proficiencies=["Medicine", "Religion"],
    tool_proficiencies=["Herbalism kit"],
    languages=1,
    equipment=["Holy symbol", "Prayer beads", "Traveler's clothes", "5 gp"],
    feature=BackgroundFeature(
        "Sacred Journey",
        "Temples and shrines along pilgrimage routes will offer you shelter, and fellow pilgrims share information freely."
    ),
    ability_score_options=["Constitution", "Wisdom", "Charisma"],
    origin_feat="Healer",
)

GLADIATOR = Background(
    name="Gladiator",
    description="You fought for crowds in arenas, pits, or staged combats. Victory brought fame while defeat meant pain or death.",
    skill_proficiencies=["Acrobatics", "Performance"],
    tool_proficiencies=["One type of musical instrument", "Disguise kit"],
    equipment=["Costume", "Unusual weapon (trophy)", "Common clothes", "15 gp"],
    feature=BackgroundFeature(
        "Arena Fame",
        "You can find fighting pits and arenas where your reputation earns you attention, challenges, and sometimes free lodging."
    ),
    ability_score_options=["Strength", "Dexterity", "Charisma"],
    origin_feat="Savage Attacker",
)

SCOUT = Background(
    name="Scout",
    description="You served as eyes and ears for military forces or settlements, ranging ahead to gather intelligence and warn of threats.",
    skill_proficiencies=["Nature", "Stealth"],
    tool_proficiencies=["Cartographer's tools"],
    languages=1,
    equipment=["Leather armor", "Hunting trap", "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Pathfinder",
        "You can recall terrain you've traveled and find efficient routes. You rarely get lost in wilderness you've explored."
    ),
    ability_score_options=["Dexterity", "Constitution", "Wisdom"],
    origin_feat="Alert",
)

COURTIER = Background(
    name="Courtier",
    description="You navigated the intrigues of noble courts, learning to read political currents and speak with careful diplomacy.",
    skill_proficiencies=["Insight", "Persuasion"],
    languages=2,
    equipment=["Fine clothes", "Signet ring or badge of office", "25 gp"],
    feature=BackgroundFeature(
        "Court Connections",
        "You understand court etiquette and can gain audiences with minor nobles. You know who holds real power in political circles."
    ),
    ability_score_options=["Intelligence", "Wisdom", "Charisma"],
    origin_feat="Skilled",
)

HAUNTED = Background(
    name="Haunted One",
    description="A terrible experience left its mark on you. You witnessed horrors that others cannot comprehend, and shadows follow you still.",
    skill_proficiencies=["Arcana", "Investigation"],
    languages=2,
    equipment=["Monster hunter's pack", "Trinket of dark origin", "Common clothes", "1 gp"],
    feature=BackgroundFeature(
        "Heart of Darkness",
        "Those who look into your eyes see someone who has faced true horror. Common folk may fear you, but they won't stand in your way."
    ),
    ability_score_options=["Constitution", "Intelligence", "Wisdom"],
    origin_feat="Magic Initiate (Wizard)",
)

SMUGGLER = Background(
    name="Smuggler",
    description="You made a living moving goods past authorities and across borders. Discretion and quick thinking kept you out of prison.",
    skill_proficiencies=["Deception", "Stealth"],
    tool_proficiencies=["Vehicles (water)", "Thieves' tools"],
    equipment=["Dark common clothes with hood", "Belt pouch with hidden compartment", "15 gp"],
    feature=BackgroundFeature(
        "Secret Routes",
        "You know hidden paths, secret docks, and contacts who can move people or goods discretely for a price."
    ),
    ability_score_options=["Dexterity", "Intelligence", "Charisma"],
    origin_feat="Alert",
)

# 2024 PHB Backgrounds (Original AI-generated descriptions)
GUIDE = Background(
    name="Guide",
    description="You know the wilderness like few others, leading expeditions through dangerous terrain and helping travelers reach their destinations safely.",
    skill_proficiencies=["Stealth", "Survival"],
    tool_proficiencies=["Cartographer's tools"],
    languages=1,
    equipment=["Cartographer's tools", "Bedroll", "Traveler's clothes", "50 gp"],
    feature=BackgroundFeature(
        "Trailblazer",
        "You can find safe paths through wilderness and recall routes you've traveled. Local guides recognize your expertise."
    ),
    ability_score_options=["Dexterity", "Constitution", "Wisdom"],
    origin_feat="Magic Initiate (Druid)",
)

# Additional Expansion Backgrounds (Original AI-generated descriptions)
KNIGHT = Background(
    name="Knight",
    description="You hold a title of minor nobility and have sworn oaths of service. Honor and duty guide your actions.",
    skill_proficiencies=["History", "Persuasion"],
    tool_proficiencies=["One type of gaming set"],
    languages=1,
    equipment=["Fine clothes", "Signet ring", "Banner or token of allegiance", "25 gp"],
    feature=BackgroundFeature(
        "Knightly Regard",
        "You receive hospitality from nobility and their retainers. Common folk respect your title and station."
    ),
    ability_score_options=["Strength", "Constitution", "Charisma"],
    origin_feat="Savage Attacker",
)

INVESTIGATOR = Background(
    name="Investigator",
    description="You have a keen eye for details and a mind that pieces together clues. Solving mysteries drives you.",
    skill_proficiencies=["Insight", "Investigation"],
    tool_proficiencies=["Disguise kit", "Thieves' tools"],
    equipment=["Magnifying glass", "Evidence collection kit", "Common clothes", "10 gp"],
    feature=BackgroundFeature(
        "Official Inquiry",
        "You know how to gain access to crime scenes and records. Authorities often cooperate with your investigations."
    ),
    ability_score_options=["Intelligence", "Wisdom", "Charisma"],
    origin_feat="Alert",
)

ARCHAEOLOGIST = Background(
    name="Archaeologist",
    description="You explore ancient ruins and study lost civilizations, piecing together history from fragments left behind.",
    skill_proficiencies=["History", "Survival"],
    tool_proficiencies=["Cartographer's tools", "Navigator's tools"],
    languages=1,
    equipment=["Wooden case with maps and notes", "Bullseye lantern", "Traveler's clothes", "25 gp"],
    feature=BackgroundFeature(
        "Dusty Lore",
        "You can identify ancient ruins and artifacts, knowing their approximate age and cultural origin."
    ),
    ability_score_options=["Constitution", "Intelligence", "Wisdom"],
    origin_feat="Skilled",
)

CITY_WATCH = Background(
    name="City Watch",
    description="You served in an urban watch, patrolling streets and maintaining order. You know cities and their dangers.",
    skill_proficiencies=["Athletics", "Insight"],
    tool_proficiencies=["Vehicles (land)"],
    languages=1,
    equipment=["Uniform", "Horn", "Manacles", "10 gp"],
    feature=BackgroundFeature(
        "Watcher's Eye",
        "You can find watch posts and know how city authorities operate. Fellow watchmen share information with you."
    ),
    ability_score_options=["Strength", "Dexterity", "Wisdom"],
    origin_feat="Alert",
)

SPY = Background(
    name="Spy",
    description="You gathered secrets for a patron, living double lives and extracting information through cunning.",
    skill_proficiencies=["Deception", "Stealth"],
    tool_proficiencies=["Disguise kit", "Thieves' tools"],
    equipment=["Disguise kit", "Dark clothes", "Hidden message tools", "15 gp"],
    feature=BackgroundFeature(
        "Spy Contact",
        "You have a handler or contact who can provide intelligence and safe houses when needed."
    ),
    ability_score_options=["Dexterity", "Intelligence", "Charisma"],
    origin_feat="Alert",
)

FISHER = Background(
    name="Fisher",
    description="You made your living from lakes, rivers, or seas, hauling nets and braving weather for your catch.",
    skill_proficiencies=["History", "Survival"],
    tool_proficiencies=["Vehicles (water)"],
    languages=1,
    equipment=["Fishing tackle", "Net", "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Harvest the Waters",
        "You know how to find fishing spots and can provide food from any body of water with fish."
    ),
    ability_score_options=["Strength", "Constitution", "Wisdom"],
    origin_feat="Lucky",
)

CLAN_CRAFTER = Background(
    name="Clan Crafter",
    description="You learned your craft from a close-knit community of artisans who passed down techniques through generations.",
    skill_proficiencies=["History", "Insight"],
    tool_proficiencies=["One type of artisan's tools"],
    languages=1,
    equipment=["Artisan's tools", "Maker's mark chisel", "Traveler's clothes", "15 gp"],
    feature=BackgroundFeature(
        "Respect of the Stout Folk",
        "Crafting communities welcome you as a peer. You receive fair treatment from artisan guilds."
    ),
    ability_score_options=["Strength", "Dexterity", "Intelligence"],
    origin_feat="Crafter",
)

FACTION_AGENT = Background(
    name="Faction Agent",
    description="You serve a larger organization with goals that span regions or realms. Your loyalty is to the faction's ideals.",
    skill_proficiencies=["Insight", "Investigation"],
    tool_proficiencies=["Disguise kit"],
    languages=2,
    equipment=["Faction insignia", "Copy of faction codes", "Common clothes", "15 gp"],
    feature=BackgroundFeature(
        "Safe Haven",
        "Faction members provide shelter, information, and support. You can send messages through faction networks."
    ),
    ability_score_options=["Intelligence", "Wisdom", "Charisma"],
    origin_feat="Skilled",
)

FAR_TRAVELER = Background(
    name="Far Traveler",
    description="You come from a distant land with customs foreign to those around you. Everything here seems strange, and you seem strange to everyone.",
    skill_proficiencies=["Insight", "Perception"],
    tool_proficiencies=["One type of gaming set or musical instrument"],
    languages=1,
    equipment=["Traveler's clothes", "Jewelry from homeland", "Poorly drawn local maps", "15 gp"],
    feature=BackgroundFeature(
        "All Eyes on You",
        "Your exotic appearance draws attention. People are curious about you and eager to hear your stories."
    ),
    ability_score_options=["Dexterity", "Wisdom", "Charisma"],
    origin_feat="Lucky",
)

INHERITOR = Background(
    name="Inheritor",
    description="You received something of significance from a family member or mentor. This inheritance shapes your path.",
    skill_proficiencies=["Survival", "Arcana"],
    tool_proficiencies=["One type of gaming set or musical instrument"],
    languages=1,
    equipment=["Inheritance item", "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Inherited Legacy",
        "Your inheritance connects you to a larger story. Those who recognize it may help you or seek your aid."
    ),
    ability_score_options=["Constitution", "Intelligence", "Charisma"],
    origin_feat="Magic Initiate (Wizard)",
)

BOUNTY_HUNTER = Background(
    name="Bounty Hunter",
    description="You tracked down fugitives for payment, learning to read people and follow trails that others missed.",
    skill_proficiencies=["Insight", "Survival"],
    tool_proficiencies=["Thieves' tools", "Vehicles (land)"],
    equipment=["Manacles", "Wanted posters", "Traveler's clothes", "15 gp"],
    feature=BackgroundFeature(
        "Ear to the Ground",
        "You know how to find information about wanted individuals and can access bounty boards in most settlements."
    ),
    ability_score_options=["Strength", "Dexterity", "Wisdom"],
    origin_feat="Alert",
)

ANTHROPOLOGIST = Background(
    name="Anthropologist",
    description="You study cultures and peoples, immersing yourself in foreign societies to understand their ways.",
    skill_proficiencies=["Insight", "Religion"],
    languages=2,
    equipment=["Leather diary", "Ink and quill", "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Cultural Chameleon",
        "After observing a culture briefly, you can mimic customs well enough to avoid giving offense."
    ),
    ability_score_options=["Intelligence", "Wisdom", "Charisma"],
    origin_feat="Skilled",
)

MARINE = Background(
    name="Marine",
    description="You served in naval military forces, fighting at sea and on hostile shores. Discipline and camaraderie forged you.",
    skill_proficiencies=["Athletics", "Survival"],
    tool_proficiencies=["Vehicles (water)", "Vehicles (land)"],
    equipment=["Dagger", "Folded flag of service", "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Steady",
        "You remain calm under pressure. Others look to you for leadership in dire situations."
    ),
    ability_score_options=["Strength", "Dexterity", "Constitution"],
    origin_feat="Tough",
)

FAILED_MERCHANT = Background(
    name="Failed Merchant",
    description="Your business ventures ended in disaster, but the lessons learned shaped your resourcefulness.",
    skill_proficiencies=["Investigation", "Persuasion"],
    tool_proficiencies=["One type of artisan's tools"],
    languages=1,
    equipment=["Merchant's scale", "Ledger of debts", "Fine clothes (worn)", "5 gp"],
    feature=BackgroundFeature(
        "Supply Chain",
        "You know how commerce works and can find suppliers, fences, or markets others cannot."
    ),
    ability_score_options=["Constitution", "Intelligence", "Charisma"],
    origin_feat="Lucky",
)

GAMBLER = Background(
    name="Gambler",
    description="You live by luck and skill at games of chance. Fortune favors the bold, and you've made a life proving it.",
    skill_proficiencies=["Deception", "Insight"],
    tool_proficiencies=["One type of gaming set", "One type of gaming set"],
    equipment=["Gaming set", "Lucky charm", "Fine clothes", "15 gp"],
    feature=BackgroundFeature(
        "Never Tell Me the Odds",
        "You can find gambling dens and games of chance. Other gamblers respect your skill and share rumors."
    ),
    ability_score_options=["Dexterity", "Wisdom", "Charisma"],
    origin_feat="Lucky",
)

ATHLETE = Background(
    name="Athlete",
    description="You trained and competed in physical contests, pushing your body to its limits for glory and prizes.",
    skill_proficiencies=["Acrobatics", "Athletics"],
    tool_proficiencies=["Vehicles (land)"],
    languages=1,
    equipment=["Trophy or medal", "Athletic clothes", "Traveler's clothes", "10 gp"],
    feature=BackgroundFeature(
        "Physical Champion",
        "You're recognized in athletic circles. You can find sponsors, training facilities, and competitions."
    ),
    ability_score_options=["Strength", "Dexterity", "Constitution"],
    origin_feat="Tough",
)

# All backgrounds
ALL_BACKGROUNDS = {
    "Acolyte": ACOLYTE,
    "Anthropologist": ANTHROPOLOGIST,
    "Archaeologist": ARCHAEOLOGIST,
    "Artisan": ARTISAN,
    "Athlete": ATHLETE,
    "Bounty Hunter": BOUNTY_HUNTER,
    "Charlatan": CHARLATAN,
    "City Watch": CITY_WATCH,
    "Clan Crafter": CLAN_CRAFTER,
    "Courtier": COURTIER,
    "Criminal": CRIMINAL,
    "Entertainer": ENTERTAINER,
    "Faction Agent": FACTION_AGENT,
    "Failed Merchant": FAILED_MERCHANT,
    "Far Traveler": FAR_TRAVELER,
    "Farmer": FARMER,
    "Fisher": FISHER,
    "Folk Hero": FOLK_HERO,
    "Gambler": GAMBLER,
    "Gladiator": GLADIATOR,
    "Guard": GUARD,
    "Guide": GUIDE,
    "Guild Artisan": GUILD_ARTISAN,
    "Haunted One": HAUNTED,
    "Hermit": HERMIT,
    "Inheritor": INHERITOR,
    "Investigator": INVESTIGATOR,
    "Knight": KNIGHT,
    "Marine": MARINE,
    "Merchant": MERCHANT,
    "Noble": NOBLE,
    "Outlander": OUTLANDER,
    "Pilgrim": PILGRIM,
    "Sage": SAGE,
    "Sailor": SAILOR,
    "Scout": SCOUT,
    "Scribe": SCRIBE,
    "Smuggler": SMUGGLER,
    "Soldier": SOLDIER,
    "Spy": SPY,
    "Urchin": URCHIN,
    "Wayfarer": WAYFARER,
}


def get_background(name: str) -> Optional[Background]:
    """Get a background by name."""
    return ALL_BACKGROUNDS.get(name)


def get_all_background_names() -> list[str]:
    """Get all background names."""
    return list(ALL_BACKGROUNDS.keys())


def get_backgrounds_for_ruleset(ruleset: Optional[str] = None) -> dict[str, Background]:
    """Get backgrounds appropriate for a specific ruleset.

    Args:
        ruleset: The ruleset ID ('dnd2014', 'dnd2024', 'tov', or None for all)

    Returns:
        Dictionary of backgrounds available for the ruleset. Returns backgrounds
        matching the ruleset or with ruleset=None (universal).
    """
    if ruleset is None:
        return ALL_BACKGROUNDS.copy()

    return {
        name: bg for name, bg in ALL_BACKGROUNDS.items()
        if bg.ruleset is None or bg.ruleset == ruleset
    }


def search_backgrounds(query: str) -> list[Background]:
    """Search backgrounds by name or description.

    Args:
        query: Search string to match against background names and descriptions

    Returns:
        List of matching backgrounds
    """
    query_lower = query.lower()
    return [
        bg for bg in ALL_BACKGROUNDS.values()
        if query_lower in bg.name.lower() or query_lower in bg.description.lower()
    ]


def validate_origin_feat(background: Background) -> tuple[bool, str]:
    """Validate that a background's origin_feat references a valid feat.

    Args:
        background: The background to validate

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty.
    """
    if background.origin_feat is None:
        return True, ""

    # Import here to avoid circular imports
    from dnd_manager.data.feats import get_feat, ORIGIN_FEATS

    # Check if feat exists
    feat = get_feat(background.origin_feat)
    if feat is None:
        return False, f"Origin feat '{background.origin_feat}' not found"

    # Check if feat is an origin feat
    origin_names = [f.name.lower() for f in ORIGIN_FEATS]
    if feat.name.lower() not in origin_names:
        return False, f"Feat '{background.origin_feat}' exists but is not an origin feat"

    return True, ""


def validate_all_origin_feats() -> list[tuple[str, str]]:
    """Validate origin_feat for all backgrounds.

    Returns:
        List of (background_name, error_message) for invalid backgrounds.
    """
    errors = []
    for name, bg in ALL_BACKGROUNDS.items():
        valid, error = validate_origin_feat(bg)
        if not valid:
            errors.append((name, error))
    return errors


def get_origin_feat_for_background(background_name: str) -> Optional["Feat"]:
    """Get the origin feat associated with a background.

    Args:
        background_name: Name of the background

    Returns:
        The Feat object if found, None otherwise
    """
    from dnd_manager.data.feats import get_feat

    background = get_background(background_name)
    if background is None or background.origin_feat is None:
        return None

    return get_feat(background.origin_feat)
