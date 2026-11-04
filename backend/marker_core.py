import pandas as pd
import re
import time
import re
from decimal import Decimal, InvalidOperation, getcontext
from fractions import Fraction
import random

def natural_key(qid: str) -> int:
    m = re.search(r'\d+', qid)      # "Q10" -> "10"
    return int(m.group()) if m else 10**9

# collect as a list (not a set) and sort by the number inside "Qn"
def mark_wide_csv(in_path, out_path):
    df = pd.read_csv(in_path)  # or read_csv

    # Find all question “triples” by column prefix/suffix
    q_ids = sorted(
    [col.split('_')[-1] for col in df.columns if col.startswith('type_')],
    key=natural_key
    )
    for q in q_ids:
        outcol = f'result_{q}'
        results = []
        for _, row in df.iterrows():
            qtype    = str(row[f'type_{q}']).strip().lower()
            expected = str(row[f'expected_{q}']).strip()
            student  = str(row[f'answer_{q}']).strip()
            results.append(router(qtype, student, expected))
        df[outcol] = results
    result_cols = sorted(
        [c for c in df.columns if c.startswith('result_Q')],
        key=lambda c: natural_key(c.split('result_')[1])
    )
    other_cols = [c for c in df.columns if not c.startswith('result_Q')]
    df = df[other_cols + result_cols]
    df.to_csv(out_path, index=False)

# Example:
# mark_wide_excel('class_answers.xlsx', 'class_results.xlsx')


def normalise_number_pass(text):
    getcontext().prec = 28
    s = (text or '').strip().lower()
    s_temp = list(s)
    UNICODE_FRACS = {
        '½': Fraction(1,2), '¼': Fraction(1,4), '¾': Fraction(3,4),
        '⅓': Fraction(1,3), '⅔': Fraction(2,3),
        '⅕': Fraction(1,5), '⅖': Fraction(2,5), '⅗': Fraction(3,5),
        '⅘': Fraction(4,5),'⅙': Fraction(1,6), '⅚': Fraction(5,6),
        '⅛': Fraction(1,8), '⅜': Fraction(3,8), '⅝': Fraction(5,8),
        '⅞': Fraction(7,8)
    }
    #expands unicode fractions to ASCII mixed fractions
    for ch, frac in UNICODE_FRACS.items():
        if ch in s:
            s = s.replace(ch, f'{frac.numerator}/{frac.denominator}')
            
    #cleans percent and converts to decimal
    divby100 = False
    temp1 = list(s)
    temp2 = []
    cont_1 = False
    cont = False
    for i in range(0,len(temp1)):
        try:
            int(temp1[i])
            temp2.append(temp1[i])
        except ValueError:
            if temp1[i] == '%':
                temp2.append(temp1[i])
                try:
                    int(temp1[i+1])
                except IndexError:
                    break
                except ValueError:
                    break
            elif temp1[i] == ".":
                if temp1[i+1].isdigit() == True:
                    for j in range(0,len(temp2)):
                        check = '.'
                        if check != temp2[j]:
                            cont_1 = True
                        else:
                            cont_1 = False
                    cont = cont_1
                    if cont == True:
                        temp2.append(temp1[i])
                    
            elif temp1[i] == "/":
                temp2.append(temp1[i])
    temp = temp2
    s = temp.copy()
    check = False
    i = 0
    while check == False and i < len(temp):
        if temp[i] == '%':
            s = list(s)
            del s[i]
            s = float(''.join(s))/100
            check = True
        else:
            i += 1
    
    #convert frac into number
    temp = s_temp
    for i in range(0,len(temp)):
        if temp[i] == '/':
            a = int(temp[i-1])
            b = int(temp[i+1])
            try:
                s = int(temp[i-1])/int(temp[i+1])
            except ZeroDivisionError:
                return 'empty'
    
    try:
        s = ''.join(s)
        return s
    except TypeError:
        return s
            
def numbers_equal_pass(a_str, b_str, mode, tol):
    a_str = str(a_str)
    b_str = str(b_str)
    try:
        a = float(normalise_number_pass(a_str))
        b = float(normalise_number_pass(b_str))
    except ValueError:
        return False
    diff = abs(a-b)
    mode = mode.lower()
    if mode == 'absolute':
        return diff <= tol
    elif mode == 'relative':
        denom = max(Decimal('1e-12'), max(abs(a), abs(b)))
        return (diff/denom) <= tol
    else:
        raise ValueError('Mode must be absolute or relative')
        
def normalise(sample):
    punctuation_list = ['?','>','<','~','#','"','!','£','$','%','^','&','*','(',')','¬','|','}','{','@','+','=','-',']','[','/',',']
    sample = sample.lower()
    sample_list_num = sample.split(' ')
    sample_list_punc = list(sample)
    sample_list_punclean = [ch for ch in sample_list_punc if ch not in punctuation_list]
    
    return sample_list_punclean
    #use python library inflect to do letter to number

def answer_pass(sample,answer):
    student_ans = ''.join(sample)
    if student_ans == answer:
        return True
    else:
        return False
        
def spellcheck_pass(sample,answer):
    answer_list = list(answer) #seperates answer into characters
    counter_C = len(sample)
    n = min(len(sample),len(answer_list))
    for i in range(0,n):
        if sample[i] != answer_list[i]:
            counter_C -=1
    quo = counter_C / max(len(sample),len(answer))
    final = int(quo * 100)
    if final > 80:
        output = f"Close spelling: {final}%"
        return output
    else:
        return False
        
def list_pass(sample, answer):
    s = ''.join(sample)
    s = s.split()
    ans = answer.split()
    #print(s)
    #print(ans)
    correct = 0
    total = len(ans)
    for i in range(0,len(ans)):
        for j in range(0,len(s)):
            if s[j] == ans[i]:
                correct += 1
                break
            else:
                sc_pass = spellcheck_pass(s[j],ans[i])
                if sc_pass != False:
                    correct += 1
                    break
                else:
                    continue
    return f'{correct}/{total} correct.'
    
        
def answer_check_text(txt, answer):
    normalise_text = normalise(txt)
    test_answer = answer.lower()
    FP = answer_pass(normalise_text, test_answer)
    if FP == False:
        SP = spellcheck_pass(normalise_text, test_answer)
        return SP
    elif FP == True:
        return FP
        
def answer_check_list(txt, answer):
    normalise_text = normalise(txt)
    pass_list = list_pass(normalise_text, answer)
    return pass_list
    
def answer_check_num(txt, answer):
    numequal = numbers_equal_pass(txt, answer, 'relative', 0.001)
    return numequal

def router(tipe, student_ans, answer):
    tipe = tipe.lower()
    if tipe == 'number':
        return answer_check_num(student_ans, answer)
    elif tipe == 'list':
        return answer_check_list(student_ans, answer)
    elif tipe == 'word':
        return answer_check_text(student_ans,answer)

def _natural_key(qid: str) -> int:
    m = re.search(r'\d+', qid or "")
    return int(m.group()) if m else 10**9

def mark_wide_df(df: pd.DataFrame,
                 number_mode: str,
                 tol: float,
                 spell_threshold: int,
                 list_order_matters: bool,
                 list_delim: str) -> pd.DataFrame:

    q_ids = sorted(
        [col.split('_')[-1] for col in df.columns if col.startswith('type_')],
        key=natural_key
    )

    for q in q_ids:
        outcol = f"result_{q}"
        results = []

        for _, row in df.iterrows():
            qtype = str(row[f"type_{q}"]).strip().lower()
            expected = str(row[f"expected_{q}"]).strip()
            student = str(row[f"answer_{q}"]).strip()

            results.append(router(qtype, student, expected))

        df[outcol] = results

    result_cols = sorted(
        [c for c in df.columns if c.startswith("result_Q")],
        key=lambda c: natural_key(c.split("result_")[1])
    )
    other_cols = [c for c in df.columns if not c.startswith("result_Q")]

    return df[other_cols + result_cols]

 
#def main():
    mark_wide_csv('tests_in_stress.csv','tests_out_template_stress.csv')
    
#main()

