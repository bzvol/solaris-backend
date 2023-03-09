from flask import Flask, request, Response
import json
from emmorphpy import EmMorphPy
import re

app = Flask(__name__)
em = EmMorphPy()
grouping_pattern = re.compile(r"(?P<prev>[a-záéíőűöüóú]+\+)?(?P<word>[a-záéíőűöüóú]+)\[(?P<wordtype>[^]]+)]=")


@app.route('/api/', methods=['GET', 'POST'])
def morph_analysis():
    text = request.args.get('text')
    if len(request.args) == 0 or text is None:
        res = {"error": "Please provide a text or word."}
        return Response(res, status=400, mimetype='application/json')

    words = []
    for word in text.split():
        words.append(analyze_word(word))

    res = {'text': text, 'words': words}
    return Response(json.dumps(res), status=200, mimetype='application/json')


def analyze_word(word):
    data = dict(word=word, analyses=[])

    pos = ['/N', '/V', '/Adj', '/Adv']
    analyses = em.analyze(word)
    for analysis in analyses:
        analysis_data = dict(prefixes=[], compound_parts=[])
        matches = grouping_pattern.findall(analysis)

        i = 0
        while matches[i][2] not in pos:
            prefix, prefix_type = matches[i][1], matches[i][2]
            analysis_data['prefixes'].append({
                'part': prefix,
                'type': prefix_type
            })
            i += 1

        current_part = None
        for _, word_part, word_type in matches[i:]:
            if word_type in pos:
                if current_part is not None:
                    analysis_data['compound_parts'].append(current_part)

                current_part = {
                    'root': {'part': word_part, 'type': word_type},
                    'suffixes': []
                }
                continue

            current_part['suffixes'].append({
                'part': word_part, 'type': word_type})

        if current_part is not None:
            analysis_data['compound_parts'].append(current_part)
        data['analyses'].append(analysis_data)

    return data


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port=port)
