from src import *

class account_manager():

    def __init__(self):
        self.driver = None
        self.cwd = os.getcwd()

    def turkish_to_english(self,text):
        # Türkçe karakterleri İngilizce karakterlere dönüştür
        turkish_chars = "ğĞıİşŞüÜöÖçÇ"
        english_chars = "gGiIssUuOOCc"
        translation_table = str.maketrans(turkish_chars, english_chars)
        text = text.translate(translation_table)

        # Boşlukları alt çizgiyle değiştir
        text = text.replace(" ", "_")

        # İngilizce karakterler dışındaki tüm karakterleri kaldır
        text = ''.join(c for c in text if c.isalnum() or c == '_')

        return text.lower()  # Metni küçük harflere çevir ve geri döndür

    def get_video_title(self,video_url):
        try:
            response = requests.get(video_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title_element = soup.find("meta", property="og:title")
                if title_element:
                    video_title = title_element["content"]
                    return self.turkish_to_english(video_title)
                else:
                    print("title_element bulunamadi.")
                    return "gonna_uploaded"
            else:
                print("status code : ",response.status_code)
                return "gonna_uploaded"
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return "gonna_uploaded"

    def save_qr_code(self) -> bool:
        try:
            self.wait_element(self.driver,By.XPATH,"//div[@role='textbox']",sleep=20,print_=False)
            return "already logged in"
        except Exception as e:
            pass

        qr_code = self.wait_element(self.driver,By.XPATH,"//canvas",sleep=40,trys=2,click=False)

        if qr_code:
            qr_code = self.wait_element(self.driver,By.XPATH,"//canvas",sleep=40,trys=2,click=False)
            qr_code.screenshot("qr_code.png")
            
            while not os.path.exists("qr_code.png"): 
                time.sleep(2)
                
            return True

        else:
            self.driver.find_element(By.XPATH,'//body').screenshot('error.png')
            raise Exception("Could not find QR code, check error.png")
    
    def show_qr_code_image(self) -> bool:
        image = cv2.imread("qr_code.png")

        if image is not None:
            print("After logging in, you can close the image by pressing any key.")
            cv2.imshow("QR Code", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Image not loaded.")
            
    def login_whatsapp(self) -> bool:
        self.driver.get("https://web.whatsapp.com/")
        
        print("It is tested whether you have logged into Whatsapp before.")
        if self.wait_element(self.driver,By.XPATH,"//div[@role='textbox']",sleep=20,print_=False,trys=1):
            print("Log found, login successful.")
            return True
        
        print("Log not found, QR Code will be shown for the first login.")
        result = self.save_qr_code()
        
        if result != "already logged in":
            self.show_qr_code_image()
            
        elif not result:
            return False
        
        if self.wait_element(self.driver,By.XPATH,"//div[@role='textbox']",sleep=100,print_=False,trys=1):
            print("Login successful.")
            return True
        else:
            print("Login failed, please initialize the driver with 'headless=False' for more details.")
            return False

    ### NOT WORKING YET ###
    def download_any_video(self,url:str,website_url:str,phone_number:str) -> bool:
        f_path = os.path.join(self.cwd, "gonna_uploaded.mp4")

        if os.path.exists(f_path):
            os.remove(f_path)

        params = 'ffmpeg.exe -y -headers \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) ' + \
                'Gecko/20100101 Firefox/108.0 Host:'+ website_url +'Accept: */* Accept-Language: en-US,en;q=0.8,tr-TR;q=0.5,tr;q=0.3 ' + \
                'Accept-Encoding: gzip, deflate, br DNT: 1 Connection: keep-alive'\
                ' Cookie: locale=tr; Sec-Fetch-Dest: script Sec-Fetch-Mode: no-cors Sec-Fetch-Site: same-origin\"'\
                ' -bsf:a aac_adtstoasc -vcodec copy -c copy ' + '\"' + f_path + '\"'
        
        err_code, stdout, stderr = command_runner(params, timeout=90, encoding='utf-8', method='monitor', \
                                                        live_output=False, stdout=False, stderr=False, split_streams=True)
        if err_code == 0 and os.path.exists(f_path):
            return self.send_video()
        if   err_code ==    0: print("  Corrupted, downloading again... [error: {}]".format(err_code))
        elif err_code ==    1: print("  FFmpeg occured error... [error: {}]"        .format(err_code))
        elif err_code == -254: print("  Process timeout... [error: {}]"             .format(err_code))
        elif err_code == -252: print("  Keyboard interrupt... [error: {}]"          .format(err_code))
        else:                  print("  Invalid error... [error: {}]"               .format(err_code))
    
    def download_youtube_video(self,url:str,phone_number:str) -> bool:
        # Uncomment later
        print("Download is starting.")
        title = self.get_video_title(url)
        command = f"yt-dlp --verbose --max-filesize 2048000000 --force-overwrites -f mp4 -o {title}.mp4 {url}"
        subprocess.run(command,shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Download finished.")
        return self.send_video(phone_number,title)

    def send_video(self,phone_number:str,title:str) -> bool:
        print("Sending video from whatsapp starting.")
        while not os.path.exists(title + ".mp4"): 
            time.sleep(3)
        
        text_box = self.wait_element(self.driver,By.XPATH,"//div[@role='textbox']",sleep=30,print_=False,click=True)
        try:
            self.wait_element(self.driver,By.XPATH,"//button[@class='-Jnba']",sleep=5,print_=False,click=True)
        except:
            pass
        text_box.send_keys(phone_number)

        time.sleep(3)
        text_box.send_keys(Keys.ENTER)

        while len(self.driver.find_elements(By.XPATH,"//div[@role='textbox']")) == 1:
            text_box.send_keys(Keys.ENTER)
            time.sleep(1.5)
        chat_box = self.driver.find_elements(By.XPATH,'//div[@role="textbox"]')[-1]
            
        self.wait_element(self.driver,By.XPATH,'//span[@data-icon="attach-menu-plus"]',click=True)
        input_box = self.wait_element(self.driver,By.XPATH,'//input[@type="file"]',click=False)

        if input_box != False:
            print("Video is uploading.")
            input_box.send_keys(str(os.path.join(self.cwd, title + ".mp4")))
            send_button = self.wait_element(self.driver,By.XPATH,'//span[@data-icon="send"]',click=True,sleep=500,trys=5)
            print("Upload process is done, video is sending.")
            if send_button == False:
                print("Can't send it, trying again.")
                return self.send_video(phone_number,title)
            return True
        else:
            print("Can't find input section")
            return False

    def prepare_driver(self,headless: bool = False,page_load_str: str = "normal",data_dir:str = "") -> bool:
        try:
            if data_dir:
                self.driver = callUcDriver(headless=headless,pageLoadStrategy=page_load_str,data_directory=data_dir)
            else:
                self.driver = callUcDriver(headless=headless,pageLoadStrategy=page_load_str)
            return True
        except Exception as e:
            print(e)
            return False

    def quit_driver(self) -> bool:
        try:
            self.driver.quit()
            return True
        except:
            return False

    def random_text_generator(self,is_mail: bool = False,lenght: int = 10) -> str:
        harfler = string.ascii_letters
        kullanici_adi = ''.join(random.choice(harfler) for _ in range(lenght))
        if is_mail:
            kullanici_adi+="@gmail.com"
        return kullanici_adi

    @staticmethod
    def wait_element(driver: webdriver,element_type,element:str,click: bool = False,trys: int = 1,sleep: int = 20,print_: bool = True):
        while trys>0:
            try:
                if click:
                    WebDriverWait(driver, sleep).until(EC.presence_of_element_located((element_type,element))).click()
                else:
                    WebDriverWait(driver, sleep).until(EC.presence_of_element_located((element_type, element)))

                return driver.find_element(element_type, element)
            except:
                    trys-=1
        if print_:
            print(f"Element {element} could not be clicked.")
        return False

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def main(app):
    while True:
        with open('data.json', 'r') as json_file:
            phone_number = json.load(json_file)["phone_number"]
        
        print("Main menu:")
        print("1-Selected phone number:",phone_number)
        print("2-Send Youtube Video")
        print("3-Send File or Folder")
        choice = input("Choose option (1/2/3): ")

        if choice == '1':
            new_phone_number = input("Enter new phone number: ")
            update_phone_number(new_phone_number)
            print("Phone number updated.")
            
        elif choice == '2':
            clear_screen()
            youtube_menu(app,phone_number)
        elif choice == '3':
            clear_screen()
            file_menu(app)

def update_phone_number(new_number):
    with open('data.json', 'w') as json_file:
        data = {'phone_number': new_number}
        json.dump(data, json_file)
        print("Phone number updated successfully.")

def youtube_menu(app,phone_number):
    urls = []
    
    while True:
        print("Send YouTube Video Menu:")
        print("1- Enter URL")
        print("2- Delete last entered URL")
        print("3- List URLs")
        print("4- Start Transactions")
        print("5- Main menu")
        choice = input("Choose option (1/2/3/4): ")

        if choice == '1':
            url = input("Enter URL: ")
            urls.append(url)
            clear_screen()
            print("URL added.")
            
        elif choice == '2':
            clear_screen()
            if urls:
                print("Last URL deleted: ", urls.pop())
            else:
                print("List is empty.")

        elif choice == '3':
            print("URLs:")
            for idx, url in enumerate(urls):
                print(f"{idx + 1}. {url}")
                
        elif choice == '4':
            clear_screen()
            for idx, url in enumerate(urls):
                print(f"URL {idx +1}, sending.")
                app.send_youtube_video(url,phone_number)
        elif choice == '5':
            clear_screen()


if __name__ == "__main__":
    app = account_manager()
    #app.prepare_driver(headless=False,data_dir="src\\chrome_log")
    #if app.login_whatsapp():
    #    main(app)
    print(app.get_video_title("https://youtu.be/TovlgzTtyGY?si=qc0sEdHfx9S3bYS_"))