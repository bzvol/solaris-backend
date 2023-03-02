from flask import Flask, request, Response
import json
import hu_core_news_md as hu
from emmorphpy import EmMorphPy


app = Flask(__name__)
nlp = hu.load()
# em = EmMorphPy()

@app.route('/')
def morphology():
    if request.method != 'POST':
        # return {'error': 'Only POST requests are allowed.'}
        return Response({'error':'Only POST requests are allowed.'}, status=405)
    
    args = request.args
    word = args.get('word')
    sentence = args.get('sentence')
    if len(args == 0) or (word and sentence):
        # return {'error': 'Please provide a word or a sentence.'}
        return Response({'error':'Please provide a word or a sentence.'}, status=400)
    
    if word:
        analyses = em.stem(word)
        l = []
        for analysis in analyses:
            l.append({
                'stem': analysis[0],
                'affixes': analysis[1][1:-1].split('][')
            })
        return json.dumps(l)
            
    if sentence:
        doc = nlp(sentence)
        l = []
        for token in doc:
            l.append({
                'text': token.text,
                'lemma': token.lemma_,
                'morphology': token.morph,
                'pos': token.pos_,
                'tag': token.tag_,
                'dep': token.dep_,
            })
        return json.dumps(l)
    
    # return 400 and some error
    # return {'error': 'Something went wrong.'}
    return Response({'error':'Something went wrong.'}, status=400)


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port=port)