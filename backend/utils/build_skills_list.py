import pandas as pd, re, json
from collections import Counter

df = pd.read_csv("datasets/all_jobs.csv")
corpus = " ".join(df["description"].dropna()).lower()
words = re.findall(r'\b[a-z][a-z0-9\+\#\.]*\b', corpus)
bigrams = [words[i]+" "+words[i+1] for i in range(len(words)-1)]

# explicit skill list — expanded
SKILLS = """
python java javascript typescript go golang rust scala kotlin swift ruby php perl bash shell
react angular vue svelte nextjs html css sass tailwind bootstrap jquery
nodejs django flask fastapi spring express rails laravel gin nestjs
tensorflow pytorch keras sklearn pandas numpy scipy matplotlib huggingface
transformers langchain llm nlp bert gpt embeddings rag mlflow wandb
sql postgresql mysql sqlite mongodb redis elasticsearch cassandra dynamodb
firestore neo4j clickhouse snowflake bigquery redshift kafka spark hadoop
aws azure gcp docker kubernetes terraform ansible jenkins helm prometheus
grafana datadog splunk nginx linux unix git github gitlab bitbucket
cybersecurity penetration nmap metasploit wireshark kali owasp cryptography
figma sketch tableau powerbi looker excel jira confluence postman swagger
""".split()

# explicit bigram skills
BIGRAM_SKILLS = [
    "machine learning","deep learning","natural language processing","computer vision",
    "data science","data engineering","data analysis","data pipeline","data pipelines",
    "software engineering","full stack","back end","front end","site reliability",
    "platform engineering","cloud infrastructure","api design","system design",
    "distributed systems","microservices","large language models","neural networks",
    "reinforcement learning","object detection","time series","feature engineering",
    "model training","model deployment","prompt engineering","vector database",
    "semantic search","ci cd","version control","code review","unit testing",
    "integration testing","software development","open source","ml systems",
    "data infrastructure","data products","data scientists","data center",
    "product design","product engineering","product management","project management",
    "technical writing","solutions architect","incident response","risk management",
    "change management","program management","account management",
]

# boilerplate bigrams to exclude
JUNK = set("""
track record long term sales roles financial infrastructure global economy
accept payments infrastructure platform largest enterprises businesses millions
ambitious startups startups use payments grow staggering amount diverse perspectives
quickly growing underrepresented groups public benefit ethical implications term goals
successfully sponsor reasonable effort host frequent greatly value easiest way
donation matching safety matters email addresses identify themselves domains legitimate
ever unsure fast paced best practices reasonable accommodation market demands
high growth functional teams good fit cross functionally authentic way proven track
partner closely data driven products services talent pool inclusion belonging
broadest talent pool possible best products qualified individuals problem solving
led people believe diverse ideas foster innovation attract creatively decision making
product teams deep understanding move faster take care employee travel travel credits
dependent upon transferable skills teams bring bring ideas sexual orientation
supporting materials screen readers curious people design accessible platform helps
helps teams gender identity characteristic protected consider qualified criminal histories
personal data life whether brainstorming creating prototype translating translating designs
empowers teams streamline workflows workflows move use cases diverse thoughts
thoughts experiences opinions allows employment opportunities opportunities regardless
citizenship marital identity expression histories consistent provided reasonable
perform essential require accommodation accommodations ext modifications enable
successfully perform disabilities examples accommodations include holding interviews
accessible location location enabling enabling closed closed captioning video conferencing
conferencing ensuring readers changing personal connection video interviews interviews
additionally person onboarding data contained privacy notice align perfectly apply anyways
hiring smart smart curious added plus fast moving non technical expertise years
customer facing high performing require reasonable financial services complex technical
full name accommodation necessary paced environment third party management skills
subject matter account executive decision makers learning development enterprise customers
real estate world class include occasional sales teams health dental prior relevant
pre sales transparency disclosure hub offices objectively assessed filled remotely
localized according dental vision vision retirement family planning mental health
health wellness recharge days development stipend cell phone phone reimbursement
offers sales sales incentive eligible non non sales functional stakeholders technical concepts
customer service united states senior leadership continuously evolving rolling basis
high performance continuous improvement user facing sales cycle trade offs registered entity
technical account technical audiences exclusion list product development date list
excluded states multiple stakeholders self starter product roadmap deep expertise
deep technical apply none none applications operational excellence product strategy
product managers presentation skills financial crimes multiple teams growth technology
marketing teams complex multi identify opportunities technical teams competing priorities
least years self serve deeply understand functional collaboration full sales sales cycles
operations teams enterprise sales analytical skills translate complex software engineer
thought leadership trusted advisor next generation technical direction high value
senior leaders senior stakeholders real world emerging technologies high volume
technical solutions revenue growth matter expert growth environment user needs
indirect tax growth marketing account plans root cause technical conversations
collaboration skills value proposition technical stakeholders partnering closely
interpersonal skills product sales federal civilian technical program managing complex
key decision sales leadership detail oriented demand generation user experiences
product adoption product manager revenue targets strategic thinking high stakes
et les et des york hub staggering amount
, "san francisco", "such as", "at least", "s degree", "people who",
"work at", "at figma", "pay range", "interview process", "experience working",
"communication skills", "even if", "every single", "meet every"
""".split("\n"))
JUNK_SET = set()
for line in JUNK:
    for phrase in line.strip().split("  "):
        JUNK_SET.add(phrase.strip())

skill_set = set(SKILLS)
found_singles = [w for w in skill_set if w in Counter(words)]

# filter bigrams from corpus
bigram_freq = Counter(bigrams)
corpus_bigrams = [b for b,c in bigram_freq.most_common(400)
    if c >= 3
    and b not in JUNK_SET
    and not any(w in {"the","a","an","and","or","of","in","to","for","with","is","are","was","were","have","has","had","be","been","not","we","you","they","our","your","their","this","that","these","those","will","would","could","should","may","might","must","can","do","does","did"} for w in b.split())
    and len(b) > 5]

final = list(dict.fromkeys(found_singles + BIGRAM_SKILLS + corpus_bigrams))

with open("datasets/skills_list.json","w") as f:
    json.dump(final, f, indent=2)

print(f"Total: {len(final)}")
print("\nSingle skills:", found_singles)
print("\nTop corpus bigrams:", corpus_bigrams[:30])