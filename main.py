import pymupdf
import traceback

def identify_block(my_tup):
    try:
        ok=len(my_tup[0])==5
        int(my_tup[0])
        #title,fktkb,description,year4,year3,year2,year1 = my_tup
        
        return ok#True #title,fktkb,description,year4,year3,year2,year1
    except:
        return False
        
        

def main():
    
    
    docs = [("ste_zeh","36-ba-steglitz-zehlendorf_2024_2025.pdf"),
            ("mitte","31_ba-mitte_2024_2025.pdf"),
            ("spandau","35-ba-spandau_2024_2025.pdf"),
            ("treptow_k","39-ba-treptow-koepenick_2024_2025.pdf"),
            
            ]
    
    for doc in docs:
        print("doing",doc[0])
        sub_main(doc[0],doc[1])
        
def sub_main(preamble,filename):
    doc = pymupdf.open(filename)
    
    all_titles = {}
    for page in doc:
        t = page.get_text("text")
        text, titles = parse_raw(t)
        new_titles = {}
        for single_title in titles:
            titles[single_title]["page"] = page.number
            new_id = single_title + "_" + str(page.number)
            new_titles[new_id] = titles[single_title]
        all_titles.update(new_titles)
        
    write_output(preamble,all_titles)
    
def test_parse_raw():
    sections = []
    with open("raw.txt","r") as f:
        t = f.read()
    
    r,titles = parse_raw(t)
    with open("raw2.txt","r") as f:
        t2 = f.read()
   
    assert r == t2
    
def parse_raw(t):
    
    """
    OK. AAAAAAAAALSO.
    
    Es gibt eintr'ge, die werden "Titel" genannt.
    
    Die sind konsistent 5 stellen lang und "Ordnungsnummern" / "ints".
    
    DIE benutze ich als Split punkte für den Gesamttext.
    
    Alles was nicht Ordnungsnummer ist, folgt einem gewissen Schema:
    
    Manchmal gibt es eine sub nummer, manchmal gibt es einen kostenplan,
    dann gibt es einträge für die tatsächlichen Zahlen.
    
    Dann gibt es eine kurze und eine lange beschreibung.
    
    """
    
    titles={}
    lines = t.split("\n")
    titel_pos = []
    c=0
    for x in lines:
        
        x=x.strip()
        lengthok=len(x)==5
        try:
            isint = str(int(x))==x
        except:
            isint = False
        
        if lengthok and isint:
            
            titel_pos.append(c)
        #input()
        if "Gesamt" in x:
            titel_pos.append(c)
            c+=1
            continue
            #sections.append(titel_pos)
            #titel_pos=[]
            
        c += 1
    
    if len(titel_pos)==0:
        return "", titles
    
    c = 0
    m = len(titel_pos)
    new_lines = []
    while c < m-1:
        marker1 = titel_pos[c]
        marker2 = titel_pos[c+1]
        my_lines = lines[marker1:marker2]
        new_my_lines=[]
        c2=0
        for el in my_lines:
            #if c2< 3:
                #c2+=1
                #continue
            if False:
                # this messes with ordinary numbers
                try:
                    el=str(clean_number(el,1))
                except:
                    pass
            
            if "(neu)" in el:
                continue
                
            new_my_lines.append(el)
            
            #c2+=1
        #try:`
        if True:
            newnew_line,sub_titles = make_newnew_line(new_my_lines)
            
            
            # skip
            if newnew_line == None:
                c += 1
                continue
            
            titles.update(sub_titles)
            my_lines = ",".join(newnew_line)
        
        else:#except:
            my_lines = ",".join(new_my_lines)
            #my_lines=my_lines.replace("-,","")
        new_lines.append(my_lines)
        
        
        c += 1
    
    pre = lines[:titel_pos[0]]
    pre = "\n".join(pre)+"\n"
    
    main_lines= "\n".join(new_lines)
    
    full = ""
    #full+=pre
    full += main_lines
    
    return full,titles
    
def make_newnew_line(new_my_lines):
    newnew_line = []
    #for line in new_my_lines:
    titel = new_my_lines[0]
    try:
        str(int(titel))==titel
    except:
        return None,None
    
    if not (len(titel)==5 and str(int(titel))==titel):
        return None,None
    
    if len(new_my_lines)==0:
        return None,None
    
    if len(new_my_lines)<3:
        return None,None
        
    funktion = new_my_lines[1]
    if len(new_my_lines[2])==3:
        kp=new_my_lines[2]
        desc_ind=3
    else:
        kp=str(None)
        desc_ind=2
        
        # ok, the description can be multiple lines
        # so.
    
    ind=desc_ind
    m=len(new_my_lines)
    description=[]
    numbers=[]
    long_description=[]
    is_number=False
    is_long_description=False
    while ind < m:
        element=new_my_lines[ind]
        try:            
            number=clean_number(element,1)
            is_desc=False
            is_number=True
            
        except:
            
            if is_number:
                is_long_description=True
            is_desc=True
        #input()
        if is_desc and not is_long_description:
            description.append(element)
        
        if is_number and not is_long_description:
            numbers.append(number)
        
        if is_long_description:
            long_description.append(element)
        
        ind+=1
    description=";".join(description)
    description=description.replace("-;","")
    description=description.replace(";","")
    description = description.replace(",",";")
    long_description = " ".join(long_description)
    #long_description = long_description.replace(",",";")
    numbers = [str(number) for number in numbers]
    while len(numbers) < 4:
        numbers.append(str(0))
    newnew_line=[titel,funktion,kp,description,*numbers,long_description]
    
    titles={str(titel):{"titel":titel,"funktion":funktion,"Kb":kp,"description":description,"values":numbers,"long description":long_description}}
    return newnew_line, titles

    
def parse_page(page):
    text = page.get_text("text")
    
    with open("raw.txt","w") as f:
        f.write(text)
    return
    
    next_clear=False
    last=None
    pre_sign=1
    titles={}
    for tup in text:
        
        tup=list(tup)
        while "" in tup:
            tup.remove('')
        
        red_tup = tuple(tup[4:-2])
        red_tup = red_tup[0].split("\n")
        
        stuff = identify_block(red_tup)
       
        if "Einnahmen" in tup:
            pre_sign=1
            
        if "Ausgaben" in tup:
            pre_sign=-1
        
        good = False
        if stuff:
            next_clear = True
            
            title, something = red_tup[0],red_tup[1]
            rd2=red_tup[2]
            rd2=rd2.strip()
            if len(rd2) == 3:
                something = (something,red_tup[2])
                desc=" ".join(red_tup[3:])
            else:
                desc=" ".join(red_tup[2:])
            
            last = (title,something,desc)
            
        elif next_clear:
            next_clear = False
            red_tup = [*last,*red_tup]
            good = True
        while "" in red_tup:
            red_tup.remove('')
                
        if not good:
            continue
                    
        if len(red_tup)< 7:
            last=red_tup
            continue
            
        title,fktkb,description,year4,year3,year2,year1 = red_tup[:7]
        values = [year4,year3,year2,year1]
        values = [clean_number(x,pre_sign) for x in values]
        
        titles[title] = {"desc":description,"years":values}
    
    return titles

def write_output(preamble,titles):
    with open(preamble+"_finances.csv","w") as f:
        f.write("title,desc,2025,2024,2023,2022,pagenumber\n")
        
        for title in titles:
            title_data = titles[title]
            
            f.write(f"{title},{title_data['description']},{','.join([str(x) for x in title_data['values']])}, {title_data['page']}\n")
    return
    with open("test.html","w") as f:
        f.write(text)

def clean_number(number,sign):
    if number == '—':
        return 0
    number = number.replace(".","_")
    number = number.replace(",",".")
    number = float(number)*sign
    return number
    
if __name__=="__main__":
    test_parse_raw()
    main()
    #clean_number("402.135,52")
    
    # this works for one page.
    #parse_raw()
    
    #main()
