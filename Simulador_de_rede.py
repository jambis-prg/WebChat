import random
import sys

class Simulador_de_Perdas:
    # Simulador de rede para simular perda de pacotes com base em uma taxa de perda configurável.
    def __init__(self, taxa_de_perda=0.0):
        self.taxa_de_perda = max(0.0, min(1.0, taxa_de_perda))                                      # Garante que está entre 0 e 1
        print(f"[SimuladorDeRede] Taxa de perda configurada: {self.taxa_de_perda:.2%}")
    
    # Determina se um pacote deve ser descartado com base na taxa de perda
    def drop_packet(self):                                                                          # Determina se um pacote deve ser descartado
        return random.random() < self.taxa_de_perda
    
    # Simular a perda de um pacote e exibe informações de debug.
    def simula_perda_de_pacote(self, packet_info=""):
        if self.drop_packet():
            print(f"[SimuladorDeRede] PERDA SIMULADA: {packet_info}")
            return True
        return False
    
    @staticmethod
    # Extrair a taxa de perda dos argumentos da linha de comando
    def recolher_taxa_dos_argumentos():
        faixa_min, faixa_max = 0.0, 0.02                                                            # Padrão: 0% a 2%
        
        # Procurar por argumentos de faixa personalizada
        for i, arg in enumerate(sys.argv):
            if arg.startswith('--random-range='):
                try:
                    range_str = arg.split('=')[1]
                    if '-' in range_str:
                        min_val, max_val = map(float, range_str.split('-'))
                        faixa_min = max(0.0, min(1.0, min_val))
                        faixa_max = max(0.0, min(1.0, max_val))
                        if faixa_min > faixa_max:
                            faixa_min, faixa_max = faixa_max, faixa_min
                except (ValueError, IndexError):
                    print(f"[SimuladorDeRede] Erro ao retirar faixa aleatória: {arg}")
        
        # Gerar taxa aleatória na faixa especificada
        taxa_aleatoria = random.uniform(faixa_min, faixa_max)
        print(f"[SimuladorDeRede] Taxa de perda: {taxa_aleatoria:.2%} (faixa: {faixa_min:.1%}-{faixa_max:.1%})")
        
        # Procurar por argumentos de taxa fixa
        taxa = taxa_aleatoria                                                                      # Padrão: taxa aleatória
        for i, arg in enumerate(sys.argv):
            if arg.startswith('--loss-rate='):                                                      # Formato: --loss-rate=0.05
                try:
                    taxa = float(arg.split('=')[1])
                    return max(0.0, min(1.0, taxa))
                except (ValueError, IndexError):
                    print(f"[SimuladorDeRede] Erro ao parsear taxa de perda: {arg}")
                    continue
            
            elif arg == '--loss' and i + 1 < len(sys.argv):                                         # Formato: --loss 0.05
                try:
                    taxa = float(sys.argv[i + 1])
                    return max(0.0, min(1.0, taxa))
                except (ValueError, IndexError):
                    print(f"[SimuladorDeRede] Erro ao parsear taxa de perda: {sys.argv[i + 1]}")
                    continue
        
        return taxa