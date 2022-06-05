#!/usr/bin/python
import cgi, os, string
import cgitb; cgitb.enable()

def find_unique_filename(dir, filename):
   filename, ext = os.path.splitext(filename)

   iter = 0
   tentative = dir + filename + ext
   while os.path.exists(tentative):
      tentative = dir + filename + f"_{iter}" + ext
      iter += 1

   return tentative
   

if os.environ['REQUEST_METHOD'] == "POST":
   form = cgi.FieldStorage()
   
   # Get filename here.
   filefield = form['filename']
   if not isinstance(filefield, list):
      filefield = [filefield]

   filepath = str(form['file_path'].value)
   # Test if the file was uploaded
   for fileitem in filefield:
      if fileitem.filename:
         # strip leading path from file name to avoid
         # directory traversal attacks
         fn = os.path.basename(fileitem.filename.replace("\\", "/" ))
         file_path_complete = find_unique_filename("/etc/http-python" + filepath, fn)
         open(file_path_complete, 'wb').write(fileitem.file.read()) 


# example (redirect)
print(f"""
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={filepath}" />
  </head>
  <body>
    <p>Please follow <a href="{filepath}">this link</a>.</p>
  </body>
</html>
""")
 