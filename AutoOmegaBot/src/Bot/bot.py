class AutoOmegaBot:
    def __init__(self, urls_file, output_file, previous_year, template_file=None):
        self.urls_file = urls_file
        self.output_file = output_file
        self.previous_year = previous_year
        self.template_file = template_file
        self.urls = []
        self.results = []

    def load_urls(self):
        import pandas as pd
        
        # Cargar el archivo Excel con las URLs
        df = pd.read_excel(self.urls_file)
        self.urls = df.iloc[:, 0].dropna().tolist()  # Suponiendo que las URLs están en la primera columna

    def run_backtest(self, url):
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            # Hacer clic en el botón "New Backtest"
            page.click('#newBacktestBtn')

            # Hacer clic en el botón "YTD"
            page.click('selector_del_boton_ytd')

            # Cambiar los datos necesarios y hacer clic en "Run"
            page.fill('selector_del_input', 'nuevo_valor')  # Cambiar el valor según sea necesario
            page.click('selector_del_boton_run')

            # Esperar a que se muestre el resultado y extraer los datos
            result = page.query_selector('selector_del_resultado').inner_text()
            self.results.append(result)

            # Cerrar la página
            browser.close()

    def save_results(self):
        import pandas as pd
        
        # Guardar los resultados en un archivo Excel
        df = pd.DataFrame(self.results, columns=['Resultados'])
        df.to_excel(self.output_file, index=False)

    def execute(self):
        self.load_urls()
        for url in self.urls:
            self.run_backtest(url)
        self.save_results()