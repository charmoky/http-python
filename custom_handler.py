import http.server
import os
import copy
import urllib.parse
import select
import html
import sys
import io

from http import HTTPStatus

from thumbnail_generator import thumb_gen

img_types = [".gif"]
comp_imag_types = [".jpg", ".jpeg", ".png"]
vid_types = [".mp4", ".webm", ".mov", ".avi"]

class custom_cgi_handler(http.server.CGIHTTPRequestHandler):
    cgi_directories = ['/sandbox/cgi-bin']
    aclµdir_list = ['sandbox/cgi-bin', 'sandbox/private', 'sandbox/shared']

    def check_acl(self):
        self.user = "anon"
        path = self.translate_path(self.path)
        
        found = False
        for acl_dir in self.aclµdir_list:
            if path.find(acl_dir) != -1:
                found = True
                break

        if not found:
            print("Did not find directory in ACL")
            return True
        
        users = []
        try:
            print("Opening file " + acl_dir + "/.acl")

            with open(acl_dir + "/.acl", "r") as f:
                for line in f:
                    users.append(line.strip())
        except:
            print("Parsing users failed !")
            return False
        
        print(users)

        authorization = self.headers.get("authorization")
        if authorization:
            authorization = authorization.split()
            if len(authorization) == 2:
                import base64, binascii
                if authorization[0].lower() == "basic":
                    try:
                        authorization = authorization[1].encode('ascii')
                        authorization = base64.decodebytes(authorization).\
                                decode('ascii')
                    except (binascii.Error, UnicodeError):
                        pass
                    else:
                        authorization = authorization.split(':')
                        if len(authorization) == 2:
                            self.user = authorization[0]
        
        if self.user in users:
            return True

        return False

    def send_head(self):
        """Version of send_head that support ACL"""

        if self.check_acl():
            return http.server.CGIHTTPRequestHandler.send_head(self)
        else:
            self.send_error(
                HTTPStatus.UNAUTHORIZED,
                f"Your user '{self.user}' is not part of the ACL")


    def is_cgi(self):
        """Test whether self.path corresponds to a CGI script.
        Returns True and updates the cgi_info attribute to the tuple
        (dir, rest) if self.path requires running a CGI script.
        Returns False otherwise.
        If any exception is raised, the caller should assume that
        self.path was rejected as invalid and act accordingly.
        The default implementation tests whether the normalized url
        path begins with one of the strings in self.cgi_directories
        (and the next character is a '/' or the end of the string).
        """
        collapsed_path = http.server._url_collapse_path(self.path)
        dir_sep = collapsed_path.find('/', 1)
        while dir_sep > 0 and not collapsed_path[:dir_sep] in self.cgi_directories:
            dir_sep = collapsed_path.find('/', dir_sep+1)

        # Treat cgi dir as normal dir
        if dir_sep > 0 and dir_sep < len(collapsed_path)-1:
            head, tail = collapsed_path[:dir_sep], collapsed_path[dir_sep+1:]
            self.cgi_info = head, tail
            return True
        return False

    def run_cgi(self):
        """Execute a CGI script."""
        dir, rest = self.cgi_info
        path = dir + '/' + rest
        i = path.find('/', len(dir)+1)
        while i >= 0:
            nextdir = path[:i]
            nextrest = path[i+1:]

            scriptdir = self.translate_path(nextdir)
            if os.path.isdir(scriptdir):
                dir, rest = nextdir, nextrest
                i = path.find('/', len(dir)+1)
            else:
                break

        # find an explicit query string, if present.
        rest, _, query = rest.partition('?')

        # dissect the part after the directory name into a script name &
        # a possible additional path, to be stored in PATH_INFO.
        i = rest.find('/')
        if i >= 0:
            script, rest = rest[:i], rest[i:]
        else:
            script, rest = rest, ''

        scriptname = dir + '/' + script
        scriptfile = self.translate_path(scriptname)
        if not os.path.exists(scriptfile):
            self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "No such CGI script (%r)" % scriptname)
            return
        if not os.path.isfile(scriptfile):
            self.send_error(
                    HTTPStatus.FORBIDDEN,
                    "CGI script is not a plain file (%r)" % scriptname)
            return
        ispy = self.is_python(scriptname)
        if self.have_fork or not ispy:
            if not self.is_executable(scriptfile):
                self.send_error(
                        HTTPStatus.FORBIDDEN,
                        "CGI script is not executable (%r)" % scriptname)
                return

        # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        # XXX Much of the following could be prepared ahead of time!
        env = copy.deepcopy(os.environ)
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = self.server.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(self.server.server_port)
        env['REQUEST_METHOD'] = self.command
        uqrest = urllib.parse.unquote(rest)
        env['PATH_INFO'] = uqrest
        env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        env['SCRIPT_NAME'] = scriptname
        if query:
            env['QUERY_STRING'] = query
        env['REMOTE_ADDR'] = self.client_address[0]
        authorization = self.headers.get("authorization")
        if authorization:
            authorization = authorization.split()
            if len(authorization) == 2:
                import base64, binascii
                env['AUTH_TYPE'] = authorization[0]
                if authorization[0].lower() == "basic":
                    try:
                        authorization = authorization[1].encode('ascii')
                        authorization = base64.decodebytes(authorization).\
                                decode('ascii')
                    except (binascii.Error, UnicodeError):
                        pass
                    else:
                        authorization = authorization.split(':')
                        if len(authorization) == 2:
                            env['REMOTE_USER'] = authorization[0]
        # XXX REMOTE_IDENT
        if self.headers.get('content-type') is None:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        else:
            env['CONTENT_TYPE'] = self.headers['content-type']
        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        referer = self.headers.get('referer')
        if referer:
            env['HTTP_REFERER'] = referer
        accept = self.headers.get_all('accept', ())
        env['HTTP_ACCEPT'] = ','.join(accept)
        ua = self.headers.get('user-agent')
        if ua:
            env['HTTP_USER_AGENT'] = ua
        co = filter(None, self.headers.get_all('cookie', []))
        cookie_str = ', '.join(co)
        if cookie_str:
            env['HTTP_COOKIE'] = cookie_str
        # XXX Other HTTP_* headers
        # Since we're setting the env in the parent, provide empty
        # values to override previously set values
        for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
                'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
            env.setdefault(k, "")

        self.send_response(HTTPStatus.OK, "Script output follows")
        self.flush_headers()

        decoded_query = query.replace('+', ' ')

        if self.have_fork:
            # Unix -- fork as we should
            args = [script]
            if '=' not in decoded_query:
                args.append(decoded_query)
            nobody = http.server.nobody_uid()
            self.wfile.flush() # Always flush before forking
            pid = os.fork()
            if pid != 0:
                # Parent
                pid, sts = os.waitpid(pid, 0)
                # throw away additional data [see bug #427345]
                while select.select([self.rfile], [], [], 0)[0]:
                    if not self.rfile.read(1):
                        break
                exitcode = os.WEXITSTATUS(sts)
                if exitcode:
                    self.log_error(f"CGI script exit code {exitcode}")
                return
            # Child
            try:
                try:
                    os.setuid(nobody)
                except OSError:
                    pass
                os.dup2(self.rfile.fileno(), 0)
                os.dup2(self.wfile.fileno(), 1)
                os.execve(scriptfile, args, env)
                print(self.wfile)
            except:
                self.server.handle_error(self.request, self.client_address)
                os._exit(127)

        else:
            # Non-Unix -- use subprocess
            import subprocess
            cmdline = [scriptfile]
            if self.is_python(scriptfile):
                interp = sys.executable
                if interp.lower().endswith("w.exe"):
                    # On Windows, use python.exe, not pythonw.exe
                    interp = interp[:-5] + interp[-4:]
                cmdline = [interp, '-u'] + cmdline
            if '=' not in query:
                cmdline.append(query)
            self.log_message("command: %s", subprocess.list2cmdline(cmdline))
            try:
                nbytes = int(length)
            except (TypeError, ValueError):
                nbytes = 0
            p = subprocess.Popen(cmdline,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env = env
                    )
            if self.command.lower() == "post" and nbytes > 0:
                data = self.rfile.read(nbytes)
            else:
                data = None
            # throw away additional data [see bug #427345]
            while select.select([self.rfile._sock], [], [], 0)[0]:
                if not self.rfile._sock.recv(1):
                    break
            stdout, stderr = p.communicate(data)
            self.wfile.write(stdout)
            if stderr:
                self.log_error('%s', stderr)
            p.stderr.close()
            p.stdout.close()
            status = p.returncode
            if status:
                self.log_error("CGI script exit status %#x", status)
            else:
                self.log_message("CGI script exited OK")


    def make_file_lists(self, path):
        self.img_list = []
        self.comp_img_list = []
        self.vid_list = []
        self.file_list = []
        self.dir_list = []

        for entry in  os.scandir(path):
            if entry.is_file():

                #Ignore "hidden" files
                if entry.name.startswith("."):
                    continue

                # is image ?
                if os.path.splitext(entry.name)[1].lower() in comp_imag_types:
                    self.comp_img_list.append(entry.name)
                    continue

                if os.path.splitext(entry.name)[1].lower() in img_types:
                    self.img_list.append(entry.name)
                    continue

                # is vid ?
                if os.path.splitext(entry.name)[1].lower() in vid_types:
                    self.vid_list.append((entry.name, os.path.splitext(entry.name)[1].lower()[1:]))
                    continue

                # Skip html files
                if os.path.splitext(entry.name)[1].lower() == ".html":
                    continue

                self.file_list.append(entry.name)

            # Else add to dir list
            else:
                #Ignore "hidden" dirs 
                if entry.name.startswith("."):
                    continue
                self.dir_list.append(entry.name + "/")

        self.comp_img_list = sorted(self.comp_img_list)
        self.dir_list = sorted(self.dir_list)
        self.file_list = sorted(self.file_list)
        self.vid_list = sorted(self.vid_list)
        self.img_list = sorted(self.img_list)

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                    errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()

        self.make_file_lists(path)

        Gen_thumb = thumb_gen(path)
        Gen_thumb.make_thumbnails()

        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                'content="text/html; charset=%s">' % enc)
        r.append("""<style>
/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}

div.gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 180px;
}

div.vid_gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 480px;
}

div.gallery:hover {
  border: 1px solid #777;
}

div.gallery img {
  width: 100%;
  height: auto;
}

div.vid_gallery video {
  width: 100%;
  height: auto;
}

div.desc {
  padding: 15px;
  text-align: center;
}
</style>""")

        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append("""<form id="uploadbanner" enctype="multipart/form-data" method="post" action="/sandbox/cgi-bin/save_file.py">
<input id="fileupload" name="filename" type="file" multiple/>
<input id="filepath" name="file_path" type=hidden value="%s"/>
<input type="submit" value="submit" id="submit" />
</form>
<div id="feedback"></div>
<label id="progress-label" for="progress"></label>
<progress id="progress" value="0" max="100"> </progress>
""" % displaypath)
        r.append('<hr>\n<ul>')

        r.append("<div class=\"row\">")
        r.append("<h2> Directory List:</h2>\n")
        r.append("<li><a href=\"../\">../</a></li>\n")
        if len(self.dir_list) > 0:
            for dir in self.dir_list:
                r.append("<li><a href=\"%s\">%s</a></li>\n" % (dir, dir))
        
        if len(self.file_list) > 0:
            for file in self.file_list:
                r.append("<li><a href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\">%s</a></li>\n" % (file, file))
        r.append("</div>")
        r.append("<br>")

        if (len(self.img_list) > 0) or (len(self.comp_img_list) >0):
            r.append("<div class=\"row\">")
            r.append("<h2> Image Gallery:</h2>\n")
            for img in self.img_list:
                r.append("""<div class="gallery">""")
                r.append("<a href=\"{0}\" target=\"_blank\" rel=\"noopener noreferrer\"> <img alt=\"{0}\" src=\"{0}\"></a>".format(img))
                r.append("""</div>""")

            # Compressed images : link to real photo, display thumbnails
            for img in self.comp_img_list:
                r.append("""<div class="gallery">""")
                r.append("<a href=\"{0}\" target=\"_blank\" rel=\"noopener noreferrer\"> <img alt=\"{0}\" src=\".thumbnails/{0}\"></a>".format(img))
                r.append("""</div>""")

            r.append("</div>")
            r.append("<br>")

        if len(self.vid_list) > 0:
            r.append("<div class=\"row\">")
            r.append("<h2> Video Gallery:</h2>\n")
            for vid in self.vid_list:
                #r.append("<video controls> <source src=\"{0}\" type=\"video/{1}\"> </video>".format(vid[0].replace(' ', '%20'), vid[1]))

                #if same file exists in mp4, prefer mp4
                if vid[1] == "mov":
                    if (vid[0].replace(" ", "_").replace(".mov", ".mp4"), "mp4") in self.vid_list:
                        continue

                # check if lowres version exists
                if vid[1] == "mp4":
                    if (vid[0].replace(".mp4", "_lowres.mp4"), vid[1]) in self.vid_list:
                        continue
                    if (vid[0].replace("_lowres.mp4",".mp4"), vid[1]) in self.vid_list:
                        r.append("""<div class="vid_gallery">""")
                        r.append("<video controls=\"controls\" preload=\"none\"> <source src=\"{0}\" type={1}>  </video>".format(vid[0].replace(' ', '%20'), vid[1]))
                        r.append(f"<a href=\"{vid[0]}\" target=\"_blank\" rel=\"noopener noreferrer\">  <div class=\"desc\">%s</div></a>" % vid[0].replace("_lowres.mp4",".mp4"))
                        r.append("""</div>""")
                        continue

                r.append("""<div class="vid_gallery">""")
                r.append("<video controls=\"controls\" preload=\"none\"> <source src=\"{0}\" type={1}>  </video>".format(vid[0].replace(' ', '%20'), vid[1]))
                r.append(f"<a href=\"{vid[0]}\" target=\"_blank\" rel=\"noopener noreferrer\">  <div class=\"desc\">%s</div></a>" % vid[0])
                r.append("""</div>""")
            r.append("</div>")
            r.append("<br>")

        r.append('</ul>\n<hr>')
        r.append('\n</body>\n</html>\n')
        r.append("""<script>

    const fileUploader = document.getElementById('fileupload');
    const feedback = document.getElementById('feedback');
    const progress = document.getElementById('progress');

    const reader = new FileReader();

    fileUploader.addEventListener('change', (event) => {
        const files = event.target.files;
        const file = files[0];
        reader.readAsDataURL(file);

        reader.addEventListener('progress', (event) => {
            if (event.loaded && event.total) {
                const percent = (event.loaded / event.total) * 100;
                progress.value = percent;
                document.getElementById('progress-label').innerHTML = Math.round(percent) + '%';

                if (percent === 100) {
                    let msg = `<span style="color:green;">File <u><b>${file.name}</b></u> has been uploaded successfully.</span>`;
                    feedback.innerHTML = msg;
                }
            }
        });
    });
</script>""")
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f
