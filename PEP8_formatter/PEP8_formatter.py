import sublime
import sublime_plugin
import random
import re


def check_import(line):  # проверка импортов
    out = ""
    if (line.startswith('import')):
        aaa = re.split(r',', line)
        out += aaa[0]
        for i in range(len(aaa)-1):
            out += "\n"+"import"+aaa[i+1]
    else:
        out = line
    return out


def check_whitespace_around_operators(line):
    out = line
    out = re.sub(r'(\s+\*\s+)', r'*', out)
    out = re.sub(r'(\s+\/\s+)', r'/', out)
    return out


def check_whitespace_2(line):
    out = line
    open_bracket_index = out.find("(")
    close_bracket_index = out.rfind(")")
    if (open_bracket_index != -1):
        if (re.search(r'if\s*\(', out) is None and re.search(r'while\s*\(', out)is None):  # проверили что это не if (...)
            line_before_bracket = out[:open_bracket_index+1]
            line_before_bracket = re.sub(r'([^\s\+\=\-\/\*\>\<!])=', r'\1 =', line_before_bracket)
            line_before_bracket = re.sub(r'=([^\s\+\=\-\/\*\>\<])', r'= \1', line_before_bracket)
            line_after_bracket = out[close_bracket_index:]
            line_after_bracket = re.sub(r'([^\s\+\=\-\/\*\>\<!])=', r'\1 =', line_after_bracket)
            line_after_bracket = re.sub(r'=([^\s\+\=\-\/\*\>\<])', r'= \1', line_after_bracket)
            out = line_before_bracket + re.sub(r'\s\=\s', r'=', out[open_bracket_index+1:close_bracket_index]) + line_after_bracket
        else:
            out = re.sub(r'([^\s\+\=\-\/\*\>\<!])=', r'\1 =', out)
            out = re.sub(r'=([^\s\+\=\-\/\*\>\<])', r'= \1', out)
    else:
        out = re.sub(r'([^\s\+\=\-\/\*\>\<!])=', r'\1 =', out)
        out = re.sub(r'=([^\s\+\=\-\/\*\>\<])', r'= \1', out)
    out = re.sub(r'([^\s\+\=\-\/\*\>\<])\+', r'\1 +', out)
    out = re.sub(r'\+([^\s\+\=\-\/\*\>\<])', r'+ \1', out)  # a+b
    out = re.sub(r'([^\s\+\=\-\/\*\>\<])-', r'\1 -', out)  # a-b
    out = re.sub(r'([^\s\+\=\-\/\*\>\<])!', r'\1 !', out)  # a!=b
    out = re.sub(r'([^\s\+\=\-\/\*\>\<])>', r'\1 >', out)
    out = re.sub(r'>([^\s\+\=\-\/\*\>\<])', r'> \1', out)  # a>b
    out = re.sub(r'([^\s\+\=\-\/\*\>\<])<', r'\1 <', out)
    out = re.sub(r'<([^\s\+\=\-\/\*\>\<])', r'< \1', out)  # a<b
    return out


def check_whitespace_after_comma(line):  # чекаем что есть пробел после запятой
    out = line
    out = re.sub(r',(\S)', r', \1', out)
    out = re.sub(r',\s{2,}', ', ', out)
    return out


def check_None_comparison(line):  # чекаем что нет сравнения с None
    out = line
    out = re.sub(r'(\w+)\s*!=\s*None', r'\1 is not None', out)
    out = re.sub(r'(\w+)\s*==\s*None', r'\1 is None', out)
    return out


def check_startsWith(line):  # чекаем что используется startswith а не срезы
    out = line
    out = re.sub(r'(\w+)\[:\d+\] == (\w+)', r'\1.startswith(\2)', out)
    out = re.sub(r'(\w+)\[:-\d+\] == (\w+)', r'\1.endswith(\2)', out)
    return out


def check_comparison_with_True(line):  # чекаем что нет (if someStuff == True)
    out = line
    out = re.sub(r'(\w+)\s*==\s*True', r'\1', out)
    out = re.sub(r'(\w+)\s+is\s+True', r'\1', out)
    return out


def check_space_before_colonAndComma(line):  # чекаем что нет пробелов перед запятой или двоеточием
    out = line
    out = re.sub(r'(\w+)\s+,', r'\1,', out)
    out = re.sub(r'(\w+)\s+:', r'\1:', out)
    return out


def check_multiple_space_around_operators(line):  # чекаем что нет (a     =   b)
    out = line
    out = re.sub(r'\s{2,}([\=\-\+\*\/\%])', r' \1', out)
    out = re.sub(r'([\=\-\+\*\/\%])\s{2,}', r'\1 ', out)
    return out


def check_two_spaces_before_inline_comment(line):  # чекаем два отступа преед комментарием
    out = line
    out = re.sub(r'(\w+)\s*#', r'\1  #', out)
    return out


def check_space_after_hashtag(line):
    out = line
    out = re.sub(r'#\s*(\w+)', r'# \1', out)
    return out


def check_str_length(line):
    out = line
    if (len(line) > 79):
        if (out.find("if") != -1):
            current_index = 0
            bracketIndex = out.find("if")
            while (len(out) - current_index > 79):
                andIndex = out.find("and", current_index)
                if (andIndex == -1):
                    break
                current_index = andIndex+3
                out = out[:andIndex]+"and"+"\n"+" "*(bracketIndex+2)+out[andIndex+3:]
    return out


def check_str_length_2(line):
    out = ""
    out += line[:len(line)-len(line.lstrip('\n'))]
    line = line.lstrip('\n')  # убрали перенос в начале строки который появляется после проверки check_two_newlines
    while (len(line) > 79):
        current_new_line_index = 0
        first_comma = line.find(',')
        if (first_comma != -1):
            first_bracket = line[:first_comma].rfind("(")
            if (first_bracket != -1):
                first_close_bracket = first_bracket + line[first_bracket:].find(")")
                out += line[:first_bracket]
                bracket_expr = line[first_bracket:first_close_bracket]
                bracket_expr = re.sub(r',\s+', r',', bracket_expr)  # убрали пробелы после запятых
                for i in bracket_expr:
                    if (i != ','):
                        out += i
                    else:
                        out += ','+'\n' + ' '*(first_bracket+1)
                current_new_line_index += first_close_bracket
                line = line[current_new_line_index:]
        if (current_new_line_index == 0):  # проверка что мы не смогли разделить строку на несколько
            break
    out += line
    return out


def check_semicolon_use(line):  # чекаем что не используется точка с запятой для нескольких команд в одной строчке
    out = line
    space_level = len(line)-len(line.lstrip(' '))
    out = re.sub(r';\s*', '\n'+' '*space_level, out)
    return out


def count_spaces(line):
    return len(line)-len(line.lstrip(' '))


def check_instance_comparison(line):  # проверка что используется isinstance
    out = line
    out = re.sub(r'type\((\w+)\) is type\((\w+)\)', r'isinstance(\1, \2)', out)
    return out


def check_whitespace_after_bracket(line):  # проверяем что нет func(   a, b  )
    out = line
    out = re.sub(r'\(\s+', '(', out)
    out = re.sub(r'\s+\)', ')', out)
    out = re.sub(r'\{\s+', '{', out)
    out = re.sub(r'\s+\}', '}', out)
    out = re.sub(r'\[\s+', '[', out)
    out = re.sub(r'\s+\]', ']', out)
    return out


def check_whitespace_before_bracket(line):  # проверяем что нет spam (1)
    out = line
    out = re.sub(r'(\w+)\s+\(', r'\1(', out)
    out = re.sub(r'(\w+)\s+\[', r'\1[', out)
    return out


def set_two_blank_lines_before_def(line):
    if (line.startswith("def") or line.startswith("class")):
        return "\n\n" + line
    elif (re.match(r'\s+def', line) is not None):
        return "\n" + line
    else:
        return line


def remove_user_newlines(lines_list):  # здесь мы убираем все переносы исходного текста
    index = 0
    out_list = []
    while (index < len(lines_list)):
        line = lines_list[index]
        if (line.count('(') > line.count(')')):
            current_index = index
            while (lines_list[current_index].count('(') >= lines_list[current_index].count(')')):
                current_index += 1
                line = line.rstrip()
                line += lines_list[current_index].lstrip(' ')
            lines_list[index] = line
            index = current_index
        index += 1
        out_list.append(line)
    return out_list


def remove_user_empty_lines(lines_list):
    out_list = []
    for i in lines_list:
        if (len(i) != 0):
            out_list.append(i)
    return out_list


def extract_comment(line):
    out = line
    comment = re.search(r'#.+', out)
    if (comment is not None):
        if (re.match(r'\s+#', out)is not None):  # комментарий - это встрочный блок
            out = re.sub(r'#\s*', r'#', out)
        else:
            out = re.sub(r'\s*#\s*', r'#', out)
        comment = re.search(r'#(.+)', out)
        out = re.sub(r'#.+', r'_#_', out)
        return comment.group(1), out
    else:
        return "", out


def paste_comment(comment, line):
    out = line
    if (re.search(r'_#_', out) is not None):
        if (re.match(r'\s*_#_', out)is not None):  # проверили а что если это блок комментариев а не встрочный
            out = re.sub(r'_#_', '# '+comment, out)
        else:
            out = re.sub(r'\s*_#_', '  # ' + comment, out)
    return out


def extract_dockstrings(code):  # убираем докстринги
    formatted_code = []
    current_index = 0
    counter = 0
    dockstrings = []
    while(current_index < len(code)):
        line = code[current_index]
        if (re.search(r'\"\"\"', line)is not None):
            current_index += 1
            while(re.search(r'\"\"\"[\s\S]+\"\"\"', line) is None and current_index < len(code)):
                line += "\n"
                line += code[current_index]
                current_index += 1
            docstr = re.search(r'\"\"\"([\s\S]+)\"\"\"', line)
            docstr = docstr.group(1)
            dockstrings.append(docstr)
            line = re.sub(r'\"\"\"[\s\S]+\"\"\"', '_doc'+str(counter)+'_', line)
            counter += 1
        else:
            current_index += 1
        formatted_code.append(line)
    return formatted_code, dockstrings


def paste_docstring(line, dockstrings):
    if (re.search(r'_doc\d+_', line)is not None):
        index = re.search(r'_doc(\d+)_', line).group(1)
        index = int(index)
        line = re.sub(r'_doc\d+_', "\"\"\""+dockstrings[index]+"\"\"\"", line)
    return line


class formatterCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        code = contents.split('\n')
        code, docstrings = extract_dockstrings(code)
        code = remove_user_newlines(code)
        code = remove_user_empty_lines(code)
        output = ""
        for i in range(len(code)):
            line = code[i]
            comment, line = extract_comment(line)
            line = check_import(line)
            line = check_None_comparison(line)  # чекать надо перед проверкой операторов
            line = check_startsWith(line)
            line = check_comparison_with_True(line)
            line = check_space_before_colonAndComma(line)
            line = check_multiple_space_around_operators(line)
            line = check_str_length(line)
            line = check_semicolon_use(line)
            line = check_instance_comparison(line)
            line = check_whitespace_after_bracket(line)
            line = check_whitespace_before_bracket(line)  # проверка пробела перед скобкой
            line = check_whitespace_after_comma(line)  # нужно проверять после проверки  пробела перед скобкой
            line = check_whitespace_2(line)  # нужно проверять после проверки пробела перед скобкой
            line = set_two_blank_lines_before_def(line)
            line = check_str_length_2(line)  # это нужно в последнюю очередь проверять
            line = paste_comment(comment, line)
            line = paste_docstring(line, docstrings)
            output += line+'\n'
        self.view.replace(edit, sublime.Region(0, self.view.size()), output)
