# analytica

FORM DATA Can resue for other specific files
FORM FIELDS
pdf_path = forms.FileField(label='Choose PDF file',widget=forms.FileInput(attrs={'accept':'application/pdf'}))

can have validate required
def init(self, ^args, ^^kwargs): super(VideoForm, self).init(^args, ^^kwargs) for session, field in self.fields.items(): field.required = True

clean data
def clean_title(self): p=self.cleaned_data['title'] if p == 'arunmaan': raise forms.ValidationError('we have a problem here') return p

 def clean_file(self):
     file = self.cleaned_data.get("file", False)
     filetype = magic.from_buffer(file.read())
     if not "XML" in filetype:
         raise ValidationError("File is not XML.")
     return file
----------------
$( "#id_proceeding_date" ).datepicker({ dateFormat: 'yy-mm-dd', changeMonth: true, changeYear: true, minDate: 0, });

************* WORKING form with validation ****************
class ContactForm(forms.Form): name = forms.CharField(required=False,max_length=30) file_path = forms.FileField(label='Please chooses') email = forms.EmailField(required=False,max_length=254) message = forms.CharField(required=False,max_length=2000,widget=forms.Textarea())

def clean_name(self): name = self.cleaned_data['name'] if name =='arunmaan': raise forms.ValidationError("This name is not allowed") return name

def clean(self): cleaned_data = super(ContactForm, self).clean() file = cleaned_data.get('file_path') valid_extensions = ['.pdf'] if file: filename = file.name ext = os.path.splitext(filename)[1] ext = ext.lower() print(filename) print(ext) if filename.endswith('.pdf'): print('File is a pdf') else: print('File is NOT a pdf') raise forms.ValidationError('You have selected '+ext+' file which is not supported please choose PDF file ') return file
