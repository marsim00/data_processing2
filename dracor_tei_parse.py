import xml.sax as xs
import os

class XMLHandler(xs.handler.ContentHandler):
    def __init__(self, output):

        super(XMLHandler, self).__init__()

        self.text_tags = ["p", "head", "speaker", "stage", "l", "emph"]  # tags that just capture text
        self.meta_tags = ["sp", "set"]  # tags that capture some tags inside them and provide extra information (like speaker_id)

        self.text_tag = "" #for text-tag
        self.meta_tag = "" #for meta-tag
        self.text_start = "" #the start of the drama

        self.fragment = {} #a dictionary to fill with meta-tag as a key and text inside as a value (e.g. key = speakers id, value = their speach)
        self.fragment_text = [] #a list with lines (just text or a speech) - becomes a value of a self.fragment if inside the meta-tag, or added just as it is
        self.drama_text = [] #a list with all the text from one drama (filled with self.fragment and fragment_text

        self.drama_id = "" #the id of a drama
        self.speaker_id = ""

        self.output = output #a dictionary filled with all dramas: the key = drama_id, the value = drama_text

    def startElement(self, xml_tag, attrs):
        #what to do at starting xml tags (<tag>)

        if xml_tag == "body": self.text_start = xml_tag #if tag is body, then the drama text has started
        if xml_tag == "TEI": self.drama_id = attrs["xml:id"] #if tag is TEI, record the drama id from its attributes

        if self.text_start: #to do if text has begun (after <body>)
            if xml_tag in self.text_tags:
                self.text_tag = xml_tag
                if xml_tag == "stage": self.fragment_text.append("$") #mark stage descriptions with $ at the beginning of the stage

            elif xml_tag in self.meta_tags: #to do if a meta_tag
                if xml_tag == "sp":
                    self.meta_tag = xml_tag
                    if attrs and "who" in attrs: self.speaker_id = attrs["who"] #get the speaker id
                elif xml_tag == "set":
                    self.meta_tag = xml_tag

    def endElement(self, xml_tag):
        #what to do at the ending xml tags (</tag>)

        if xml_tag == "stage" and self.fragment_text: self.fragment_text += ["@"] #mark stage with @ at its end

        if xml_tag == self.meta_tag: #if the current ending xml-tag equals the one that is stored in self.meta-tag (it was stored at the starting meta-tag)
            self.text_tag = "" #clear the text tag
            if xml_tag == "sp": #if the speech has ended, then assign the speech to the fragment dict with a key "sp_#speaker_id"
                self.fragment[self.meta_tag+"_"+self.speaker_id] = self.fragment_text
            else:
                self.fragment[self.meta_tag] = self.fragment_text #if it was set, then assign to the set
            self.drama_text.append(self.fragment) #add the resulting dictionary to the list of the drama

            #clear everything
            self.fragment = {}
            self.fragment_text = []
            self.meta_tag = ""

        elif xml_tag==self.text_tag: #if xml tag closes current text tag
            if not self.meta_tag: #and in case self.meta_tag is not empty (it's not the speech or a set)
                self.drama_text.append(self.fragment_text) #add the fragment to the drama text

                #clear everything
                self.text_tag=""
                self.fragment_text = []

        elif xml_tag == "text": # if the drama has ended
            self.output[self.drama_id] = self.drama_text #assign text to the output dictionary with  a drama id as a key
            self.text_tag = "" #clear text tag

    def characters(self, content):
        #to do with text between tags

        if self.text_tag: #if text_tag is stored
            if not content.isspace():
                self.fragment_text.append(content.strip()) # add line to the list only if its not empty

parsed_drama_dict = {} #the empty dictionary to be filled with parsed dramas
drama_files = os.listdir("tei") #get names of all tei-drama feils and write them in the list

#create the dictionary with dramas using the parser
for drama in drama_files:
    print(drama)
    xs.parse("tei/"+drama, XMLHandler(output=parsed_drama_dict))

#write parsed dramas to the one text file
with open("parsed_tei/parsed_dracor", "a", encoding="utf-8") as file:
    for drama_id in parsed_drama_dict:
        #at the beginning of each drama write the line "$id_" and drama id
        file.write("$id_"+"".join(drama_id)+"\n")
        for fragment in parsed_drama_dict[drama_id]:
            #write fragments stored as simple lists
            if type(fragment)==list:
                for txt in fragment:
                    file.write(txt+ "\n")
            else: #write fragments stored as dictionaries (mostly speech)
                #at the beginning of each speech write "$" and speaker id
                file.write("$"+"".join(fragment) + "\n")
                for value in fragment.values():
                    for txt in value:
                        file.write(txt+"\n")
                file.write("@"+"".join(fragment) + "\n") #at the end "@" and speaker id
        file.write("@id_" + "".join(drama_id) + "\n") #at the end of the drama write "@id_" and drama id