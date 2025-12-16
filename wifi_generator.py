import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import io
import os
import sys
import platform
import subprocess
import segno
from segno import helpers

# --- Importações para o PDF ---
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# --- Importações para Impressão no Windows ---
try:
    import win32print
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# --- FUNÇÃO AUXILIAR PARA RECURSOS ---
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class WifiQRCodeApp:
    def __init__(self, master):
        self.master = master
        master.title("Gerador de QR Code Wi-Fi")
        master.resizable(False, False)

        # Variáveis de controle
        self.ssid_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.security_var = tk.StringVar(value="WPA/WPA2")
        self.mostrar_senha_var = tk.BooleanVar(value=False)

        # Componentes visuais
        self._criar_widgets_formulario()
        self._criar_widget_qrcode()

    def _criar_widgets_formulario(self):
        frame_input = ttk.Frame(self.master, padding="10 10 10 10")
        frame_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame_input, text="Configurações da Rede", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(frame_input, text="Nome da Rede (SSID):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame_input, width=30, textvariable=self.ssid_var).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        ttk.Label(frame_input, text="Senha:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_pass = ttk.Entry(frame_input, width=22, textvariable=self.password_var, show="*")
        self.entry_pass.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        cb_mostrar = ttk.Checkbutton(frame_input, text="👁️", variable=self.mostrar_senha_var, command=self.alternar_visualizacao_senha)
        cb_mostrar.grid(row=2, column=2, padx=0, pady=5, sticky="w")

        ttk.Label(frame_input, text="Segurança:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        segurancas = ["WPA/WPA2", "WEP", "Sem Senha (Aberto)"]
        self.combobox_seg = ttk.Combobox(frame_input, textvariable=self.security_var, values=segurancas, state="readonly", width=27)
        self.combobox_seg.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        self.combobox_seg.set("WPA/WPA2")

        ttk.Button(frame_input, text="Atualizar Preview", command=self.gerar_qrcode).grid(row=4, column=0, columnspan=3, pady=20)

        self.ssid_var.trace_add("write", lambda *args: self.gerar_qrcode())
        self.password_var.trace_add("write", lambda *args: self.gerar_qrcode())
        self.security_var.trace_add("write", lambda *args: self.gerar_qrcode())

    def alternar_visualizacao_senha(self):
        if self.mostrar_senha_var.get():
            self.entry_pass.config(show="")
        else:
            self.entry_pass.config(show="*")

    def _criar_widget_qrcode(self):
        frame_output = ttk.Frame(self.master, padding="10 10 10 10")
        frame_output.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame_output, text="QR Code para Conexão", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.label_qrcode = ttk.Label(frame_output, text="Preencha os dados", background='white', relief=tk.SUNKEN, width=30)
        self.label_qrcode.pack(pady=10, padx=10)
        
        ttk.Button(frame_output, text="Salvar Imagem (PNG)", command=self.salvar_qrcode_png).pack(pady=5, fill=tk.X)
        ttk.Button(frame_output, text="👁️ Visualizar PDF", command=self.visualizar_pdf).pack(pady=5, fill=tk.X)
        ttk.Button(frame_output, text="Salvar Placa PDF", command=self.salvar_placa_pdf).pack(pady=5, fill=tk.X)
        ttk.Button(frame_output, text="🖨️ Imprimir Placa", command=self.iniciar_impressao).pack(pady=5, fill=tk.X)
        
        self.status_label = ttk.Label(self.master, text="", foreground='blue')
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)

    def gerar_qrcode(self):
        ssid = self.ssid_var.get()
        password = self.password_var.get()
        security_text = self.security_var.get()
        
        if not ssid:
            self.label_qrcode.config(image='', text="Preencha o SSID")
            return

        if "Sem Senha" in security_text:
            security = None
            password = None
        elif "WEP" in security_text:
            security = "WEP"
        else:
            security = "WPA"

        try:
            self.qrcode_wifi = helpers.make_wifi(ssid=ssid, password=password, security=security)
            buffer = io.BytesIO()
            self.qrcode_wifi.save(buffer, kind='png', scale=8, border=2)
            buffer.seek(0)
            image = Image.open(buffer)
            self.tk_image = ImageTk.PhotoImage(image)
            self.label_qrcode.config(image=self.tk_image, text="")
            self.status_label.config(text="Preview atualizado.", foreground="black")
        except Exception as e:
            self.status_label.config(text=f"Erro: {e}", foreground='red')

    def salvar_qrcode_png(self):
        ssid = self.ssid_var.get()
        if not ssid or not hasattr(self, 'qrcode_wifi'):
            self.status_label.config(text="Gere o QR Code primeiro!", foreground='orange')
            return
        filename = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"wifi_{ssid}.png", filetypes=[("PNG files", "*.png")])
        if filename:
            try:
                self.qrcode_wifi.save(filename, scale=10, border=4)
                self.status_label.config(text=f"PNG salvo!", foreground='green')
            except Exception as e:
                self.status_label.config(text=f"Erro: {e}", foreground='red')

    def _criar_arquivo_pdf(self, filename):
        """Gera o arquivo PDF no caminho especificado."""
        ssid = self.ssid_var.get()
        password = self.password_var.get()
        
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        centro_x = width / 2
        
        # --- Definindo a Moldura ---
        margem_frame = 20 * mm
        largura_frame = width - (2 * margem_frame)
        altura_frame = 230 * mm
        topo_frame = height - margem_frame
        # Calculamos a base da moldura para usar no logo depois
        base_frame_y = topo_frame - altura_frame
        
        c.setLineWidth(5)
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(margem_frame, base_frame_y, largura_frame, altura_frame, stroke=1, fill=0)
        
        y_atual = topo_frame - 40 * mm

        # --- Ícone Wi-Fi ---
        c.setLineWidth(4)
        c.setLineCap(1)
        c.circle(centro_x, y_atual, 1.5 * mm, fill=1)
        
        p = c.beginPath()
        p.arc(centro_x - 8*mm, y_atual - 8*mm, centro_x + 8*mm, y_atual + 8*mm, 45, 90)
        c.drawPath(p)
        p = c.beginPath()
        p.arc(centro_x - 14*mm, y_atual - 14*mm, centro_x + 14*mm, y_atual + 14*mm, 45, 90)
        c.drawPath(p)
        p = c.beginPath()
        p.arc(centro_x - 20*mm, y_atual - 20*mm, centro_x + 20*mm, y_atual + 20*mm, 45, 90)
        c.drawPath(p)
        
        y_atual -= 25 * mm

        # --- Textos Superiores ---
        c.setFont("Helvetica-Bold", 45)
        c.drawCentredString(centro_x, y_atual, "W I F I")
        y_atual -= 15 * mm

        c.setFont("Helvetica", 14)
        c.drawCentredString(centro_x, y_atual, "E S C A N E I E   P A R A   C O N E C T A R")
        
        y_atual -= 85 * mm 

        # --- QR Code ---
        temp_qr_file = "temp_qr_for_pdf.png"
        if hasattr(self, 'qrcode_wifi'):
            qr_obj = self.qrcode_wifi
        else:
            security = "WPA" if "WPA" in self.security_var.get() else ("WEP" if "WEP" in self.security_var.get() else None)
            qr_obj = helpers.make_wifi(ssid=ssid, password=password, security=security)
        
        qr_obj.save(temp_qr_file, scale=10, border=1)
        tamanho_qr = 80 * mm
        # O comando drawImage usa o canto inferior esquerdo. Ajustando para centralizar.
        c.drawImage(temp_qr_file, centro_x - (tamanho_qr/2), y_atual, width=tamanho_qr, height=tamanho_qr)
        if os.path.exists(temp_qr_file):
            os.remove(temp_qr_file)
        
        y_atual -= 20 * mm 

        # --- Informações ---
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(centro_x, y_atual, f"REDE: {ssid}")
        
        y_atual -= 8 * mm 
        display_pass = password if password else "REDE ABERTA"
        c.drawCentredString(centro_x, y_atual, f"SENHA: {display_pass}")

        # --- LOGO DO RODAPÉ (CORRIGIDO) ---
        logo_filename = "image_1.png"
        logo_path = resource_path(logo_filename)

        if os.path.exists(logo_path):
            try:
                img_pil = Image.open(logo_path)
                orig_w, orig_h = img_pil.size
                aspect_ratio = orig_h / orig_w
                
                target_width = 60 * mm
                target_height = target_width * aspect_ratio
                
                draw_x = centro_x - (target_width / 2)
                
                # --- FIX: Posicionamento Absoluto em relação à base da moldura ---
                # Define um espaçamento (padding) de 10mm acima da linha inferior da moldura
                padding_bottom = 10 * mm
                draw_y = base_frame_y + padding_bottom
                
                c.drawImage(logo_path, draw_x, draw_y, width=target_width, height=target_height, mask='auto')
            except Exception as e:
                 print(f"Erro ao processar logo: {e}")

        c.showPage()
        c.save()

    def visualizar_pdf(self):
        ssid = self.ssid_var.get()
        if not ssid:
            messagebox.showwarning("Aviso", "Preencha o nome da rede para visualizar.")
            return

        temp_view_pdf = os.path.abspath(f"preview_{ssid}.pdf")
        
        try:
            self._criar_arquivo_pdf(temp_view_pdf)
            
            if platform.system() == 'Windows':
                os.startfile(temp_view_pdf)
            elif platform.system() == 'Darwin':
                subprocess.call(('open', temp_view_pdf))
            else:
                subprocess.call(('xdg-open', temp_view_pdf))
                
            self.status_label.config(text="Abrindo visualização...", foreground='blue')
            
        except Exception as e:
            self.status_label.config(text=f"Erro ao visualizar: {e}", foreground='red')
            messagebox.showerror("Erro", f"Não foi possível abrir o visualizador de PDF.\n{e}")

    def salvar_placa_pdf(self):
        ssid = self.ssid_var.get()
        if not ssid:
            messagebox.showwarning("Aviso", "Preencha o nome da rede.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Placa_Wifi_{ssid}.pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                self._criar_arquivo_pdf(filename)
                self.status_label.config(text=f"PDF salvo!", foreground='green')
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{filename}")
            except Exception as e:
                self.status_label.config(text=f"Erro: {e}", foreground='red')

    def iniciar_impressao(self):
        ssid = self.ssid_var.get()
        if not ssid:
            messagebox.showwarning("Aviso", "Preencha o nome da rede para imprimir.")
            return

        self.temp_pdf_print = os.path.abspath("temp_print_wifi.pdf")
        try:
            self._criar_arquivo_pdf(self.temp_pdf_print)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar arquivo temporário: {e}")
            return

        if platform.system() == "Windows":
            if HAS_WIN32:
                self._abrir_janela_selecao_impressora()
            else:
                messagebox.showwarning("Atenção", "Biblioteca 'pywin32' não encontrada.\nO arquivo será aberto para você imprimir manualmente.")
                os.startfile(self.temp_pdf_print)
        else:
            try:
                subprocess.call(["xdg-open", self.temp_pdf_print])
            except:
                messagebox.showinfo("Impressão", f"O arquivo foi gerado em: {self.temp_pdf_print}.\nPor favor, abra-o e imprima.")

    def _abrir_janela_selecao_impressora(self):
        janela_print = tk.Toplevel(self.master)
        janela_print.title("Selecionar Impressora")
        janela_print.geometry("400x150")
        janela_print.grab_set()

        ttk.Label(janela_print, text="Escolha a impressora:", font=('Arial', 10)).pack(pady=10)

        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        impressoras_raw = win32print.EnumPrinters(flags)
        lista_impressoras = [p[2] for p in impressoras_raw]

        try:
            impressora_padrao = win32print.GetDefaultPrinter()
        except:
            impressora_padrao = ""

        combo_impressoras = ttk.Combobox(janela_print, values=lista_impressoras, state="readonly", width=40)
        combo_impressoras.pack(pady=5)
        
        if impressora_padrao in lista_impressoras:
            combo_impressoras.set(impressora_padrao)
        elif lista_impressoras:
            combo_impressoras.current(0)

        def confirmar_envio():
            impressora_escolhida = combo_impressoras.get()
            if not impressora_escolhida:
                return
            
            try:
                win32api.ShellExecute(
                    0,
                    "printto",
                    self.temp_pdf_print,
                    f'"{impressora_escolhida}"',
                    ".",
                    0
                )
                self.status_label.config(text=f"Enviado para: {impressora_escolhida}", foreground='green')
                janela_print.destroy()
            except Exception as e:
                messagebox.showerror("Erro de Impressão", f"Não foi possível enviar para a impressora.\nErro: {e}")

        ttk.Button(janela_print, text="🖨️ IMPRIMIR AGORA", command=confirmar_envio).pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = WifiQRCodeApp(root)
    root.mainloop()