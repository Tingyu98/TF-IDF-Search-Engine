
from flask import Flask, request, render_template
import boto3
from boto3.dynamodb.conditions import Key


app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('tfidf') 

stopwords_set = set(["a", "as", "able", "about", "above", "according", "accordingly",
      "across", "actually", "after", "afterwards", "again", "against", "aint", "all", "allow",
      "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among",
      "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway",
      "anyways", "anywhere", "apart", "appear","appreciate", "appropriate", "are", "arent", "around",
      "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "be", "became",
      "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below",
      "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but", "by", "cmon",
      "cs", "came", "can", "cant", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes",
      "clearly", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing",
      "contains", "corresponding", "could", "couldnt", "course", "currently", "definitely", "described", "despite", "did", "didnt",
      "different", "do", "does", "doesnt", "doing", "dont", "done", "down", "downwards", "during", "each",
      "edu", "eg", "eight", "either", "else", "elsewhere", "enough", "entirely", "especially", "et", "etc",
      "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except",
      "far", "few", "ff", "fifth", "first", "five", "followed", "following", "follows", "for", "former",
      "formerly", "forth", "four", "from", "further", "furthermore", "get", "gets", "getting", "given", "gives",
      "go", "goes", "going", "gone", "got", "gotten", "greetings", "had", "hadnt", "happens", "hardly",
      "has", "hasnt", "have", "havent", "having", "he", "hes", "hello", "help", "hence", "her",
      "here", "heres", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself",
      "his", "hither", "hopefully", "how", "howbeit", "however", "i", "id", "ill", "im", "ive",
      "ie", "if", "ignored", "immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates",
      "inner", "insofar", "instead", "into", "inward", "is", "isnt", "it", "itd", "itll", "its",
      "its", "itself", "just", "keep", "keeps", "kept", "know", "knows", "known", "last", "lately",
      "later", "latter", "latterly", "least", "less", "lest", "let", "lets", "like", "liked", "likely",
      "little", "look", "looking", "looks", "ltd", "mainly", "many", "may", "maybe", "me", "mean",
      "meanwhile", "merely", "might", "more", "moreover", "most", "mostly", "much", "must", "my", "myself",
      "name", "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless",
      "new", "next", "nine", "no", "nobody", "non", "none", "noone", "nor", "normally", "not",
      "nothing", "novel", "now", "nowhere", "obviously", "of", "off", "often", "oh", "ok", "okay",
      "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others", "otherwise",
      "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "particular", "particularly",
      "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", "que", "quite",
      "qv", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively",
      "right", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing",
      "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously",
      "seven", "several", "shall", "she", "should", "shouldnt", "since", "six", "so", "some", "somebody",
      "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify",
      "specifying", "still", "sub", "such", "sup", "sure", "ts", "take", "taken", "tell", "tends",
      "th", "than", "thank", "thanks", "thanx", "that", "thats", "thats", "the", "their", "theirs",
      "them", "themselves", "then", "thence", "there", "theres", "thereafter", "thereby", "therefore", "therein", "theres",
      "thereupon", "these", "they", "theyd", "theyll", "theyre", "theyve", "think", "third", "this", "thorough",
      "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too",
      "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", "un",
      "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used",
      "useful", "uses", "using", "usually", "value", "various", "very", "via", "viz", "vs", "want",
      "wants", "was", "wasnt", "way", "we", "wed", "well", "were", "weve", "welcome", "well",
      "went", "were", "werent", "what", "whats", "whatever", "when", "whence", "whenever", "where", "wheres",
      "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who",
      "whos", "whoever", "whole", "whom", "whose", "why", "will", "willing", "wish", "with", "within",
      "without", "wont", "wonder", "would", "would", "wouldnt", "yes", "yet", "you", "youd", "youll",
      "youre", "youve", "your", "yours", "yourself", "yourselves", "zero"])


def process_input(user_input):
    words = user_input.lower().split()
    cleaned_words = ["".join(filter(lambda ch: 97 <= ord(ch) <= 122, word)) for word in words]
    terms = [word for word in cleaned_words if word not in stopwords_set and word != '']
    return terms

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.form['user_input'].strip()
    terms = process_input(user_input)
    if not terms:
        return render_template('index.html', message="No valid terms in input", rows=[])

    doc_scores = {}
    query_length = len(terms)
    for term in terms:
        response = table.query(KeyConditionExpression=Key('term').eq(term))
        items = response.get('Items', [])
        for item in items:
            doc_id = item['doc_id']
            score = float(item['score'])
            if doc_id in doc_scores:
                doc_scores[doc_id] += score / query_length
            else:
                doc_scores[doc_id] = score / query_length

    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    top_docs = sorted_docs[:5]

    if top_docs:
        return render_template('index.html', rows=top_docs)
    else:
        return render_template('index.html', message="Not Found")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5330, debug=True)
    # http://54.221.180.227:5330