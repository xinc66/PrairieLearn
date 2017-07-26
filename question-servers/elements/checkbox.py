import random, lxml.html
import prairielearn as pl

def prepare(element_html, element_index, data, options):
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "name")

    correct_answers = [];
    incorrect_answers = [];
    index = 0
    for child in element:
        if child.tag == "answer":
            correct = pl.get_boolean_attrib(child, "correct", False)
            child_html = pl.inner_html(child)
            answer_tuple = (index, correct, child_html)
            if correct:
                correct_answers.append(answer_tuple)
            else:
                incorrect_answers.append(answer_tuple)

    len_correct = len(correct_answers)
    len_incorrect = len(incorrect_answers)
    len_total = len_correct + len_incorrect

    number_answers = pl.get_integer_attrib(element, "number_answers", len_total)
    min_correct = pl.get_integer_attrib(element, "min_correct", 0)
    max_correct = pl.get_integer_attrib(element, "max_correct", len(correct_answers))

    number_answers = max(0, min(len_total, number_answers))
    min_correct = min(len_correct, min(number_answers, max(0, max(number_answers - len_incorrect, min_correct))))
    max_correct = min(len_correct, min(number_answers, max(min_correct, max_correct)))
    if not (0 <= min_correct <= max_correct <= len_correct):
        raise Exception("INTERNAL ERROR: correct number: (%d, %d, %d, %d)" % (min_correct, max_correct, len_correct, len_incorrect))
    min_incorrect = number_answers - max_correct
    max_incorrect = number_answers - min_correct
    if not (0 <= min_incorrect <= max_incorrect <= len_incorrect):
        raise Exception("INTERNAL ERROR: incorrect number: (%d, %d, %d, %d)" % (min_incorrect, max_incorrect, len_incorrect, len_correct))

    number_correct = random.randint(min_correct, max_correct)
    number_incorrect = number_answers - number_correct

    sampled_correct = random.sample(correct_answers, number_correct)
    sampled_incorrect = random.sample(incorrect_answers, number_incorrect)

    sampled_answers = sampled_correct + sampled_incorrect
    random.shuffle(sampled_answers)

    fixed_order = pl.get_boolean_attrib(element, "fixed_order", False)
    if fixed_order:
        # we can't simply skip the shuffle because we already broke the original
        # order by separating into correct/incorrect lists
        sampled_answers.sort(key=lambda a: a[0]) # sort by stored original index

    display_answers = []
    true_answers = []
    for (i, (index, correct, html)) in enumerate(sampled_answers):
        keyed_answer = {"key": chr(ord('a') + i), "html": html}
        display_answers.append(keyed_answer)
        if correct:
            true_answers.append(keyed_answer)

    if name in data["params"]:
        raise Exception("duplicate params variable name: %s" % name)
    if name in data["true_answer"]:
        raise Exception("duplicate true_answer variable name: %s" % name)
    data["params"][name] = display_answers
    data["true_answer"][name] = true_answers
    return data

def render(element_html, element_index, data, options):
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "name")

    display_answers = data["params"].get(name, [])

    inline = pl.get_boolean_attrib(element, "inline", False)

    submitted_keys = data["submitted_answer"].get(name, [])
    # if there is only one key then it is passed as a string,
    # not as a length-one list, so we fix that next
    if isinstance(submitted_keys, str):
        submitted_keys = [submitted_keys]

    if options["panel"] == "question":
        editable = options["editable"]

        html = '';
        for answer in display_answers:
            item = '  <label' + (' class="checkbox-inline"' if inline else '') + '>\n' \
                    + '    <input type="checkbox"' \
                    + ' name="' + name + '" value="' + answer["key"] + '"' \
                    + ('' if editable else ' disabled') \
                    + (' checked ' if (answer["key"] in submitted_keys) else '') \
                    + ' />\n' \
                    + '    (' + answer["key"] + ') ' + answer["html"].strip() + '\n' \
                    + '  </label>\n'
            if not inline:
                item = '<div class="checkbox">\n' + item + '</div>\n'
            html += item
        if inline:
            html = '<p>\n' + html + '</p>\n'
    elif options["panel"] == "submission":
        if len(submitted_keys) == 0:
            html = "No selected answers"
        else:
            html_list = [];
            for submitted_key in submitted_keys:
                item = ''
                submitted_html = next((a["html"] for a in display_answers if a["key"] == submitted_key), None)
                if submitted_html is None:
                    item = "ERROR: Invalid submitted value selected: %s" % submitted_key
                else:
                    item = "(%s) %s" % (submitted_key, submitted_html)
                if inline:
                    item = '<span>' + item + '</span>\n'
                else:
                    item = '<p>' + item + '</p>\n'
                html_list.append(item)
            if inline:
                html = ', '.join(html_list) + '\n'
            else:
                html = '\n'.join(html_list) + '\n'
    elif options["panel"] == "answer":
        true_answers = data["true_answer"].get(name, [])
        if len(true_answers) == 0:
            html = "No selected answers"
        else:
            html_list = [];
            for answer in true_answers:
                item = "(%s) %s" % (answer["key"], answer["html"])
                if inline:
                    item = '<span>' + item + '</span>\n'
                else:
                    item = '<p>' + item + '</p>\n'
                html_list.append(item)
            if inline:
                html = ', '.join(html_list) + '\n'
            else:
                html = '\n'.join(html_list) + '\n'
    else:
        raise Exception("Invalid panel type: %s" % options["panel"])

    return html

def parse(element_html, element_index, data, options):
    return data

def grade(element_html, element_index, data, options):
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "name")
    weight = pl.get_integer_attrib(element, "weight", 1)

    submitted_keys = data["submitted_answer"].get(name, [])
    true_answers = data["true_answer"].get(name, [])
    true_keys = [answer["key"] for answer in true_answers]

    score = 0
    if set(submitted_keys) == set(true_keys):
        score = 1

    data["partial_scores"][name] = {"score": score, "weight": weight}
    return data