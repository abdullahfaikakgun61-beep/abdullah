#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türkçe Programlama Dili Yorumlayıcısı (Interpreter)
Version: 1.0 (Tam Versiyon)
Özellikleri: Fonksiyonlar, Diziler, Döngüler, Koşullar, Dosya İşlemleri, Hata Yönetimi
"""

import sys
import re
import os
from typing import Dict, List, Any, Tuple, Optional

class TurkceInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, List[str]] = {}
        self.lines: List[str] = []
        self.current_line: int = 0
        self.return_value: Any = None
        self.in_function: bool = False
        self.break_flag: bool = False
        self.continue_flag: bool = False

    def tokenize(self, code: str) -> List[str]:
        """Kodu satırlara böl ve işle"""
        lines = code.strip().split('\n')
        processed = []
        for line in lines:
            stripped = line.strip()
            # Yorum ve boş satırları çıkar
            if stripped and not stripped.startswith('#'):
                processed.append(stripped)
        return processed

    def evaluate_expression(self, expr: str) -> Any:
        """Matematiksel ve string ifadeleri değerlendir"""
        expr = expr.strip()
        
        # String kontrol
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        # Boolean kontrol
        if expr.lower() == 'doğru':
            return True
        if expr.lower() == 'yanlış':
            return False
        
        # Null/Hiçbir şey
        if expr.lower() == 'hiç':
            return None
        
        # Değişken kontrol
        if expr in self.variables:
            return self.variables[expr]
        
        # Sayı kontrol
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass
        
        # Dizi indexi (x[0])
        if '[' in expr and ']' in expr:
            match = re.match(r'(\w+)\[(\d+)\]', expr)
            if match:
                array_name = match.group(1)
                index = int(match.group(2))
                if array_name in self.variables:
                    arr = self.variables[array_name]
                    if isinstance(arr, (list, str)) and 0 <= index < len(arr):
                        return arr[index]
        
        # Matematiksel işlem ve mantıksal ifadeler
        try:
            # Değişkenleri değerle
            for var_name, var_value in self.variables.items():
                if isinstance(var_value, str):
                    expr = re.sub(r'\b' + var_name + r'\b', f'"{var_value}"', expr)
                else:
                    expr = re.sub(r'\b' + var_name + r'\b', str(var_value), expr)
            
            # Türkçe operatörler
            expr = expr.replace(' ve ', ' and ')
            expr = expr.replace(' veya ', ' or ')
            expr = expr.replace(' değil ', ' not ')
            expr = expr.replace('≠', '!=')
            expr = expr.replace('≤', '<=')
            expr = expr.replace('≥', '>=')
            
            # Boole dönüştür
            expr = expr.replace('doğru', 'True')
            expr = expr.replace('yanlış', 'False')
            
            result = eval(expr)
            return result
        except Exception as e:
            return expr

    def get_string_value(self, expr: str) -> str:
        """String değeri al"""
        value = self.evaluate_expression(expr)
        if value is None:
            return ""
        return str(value)

    def execute_line(self, line: str) -> bool:
        """Tek bir satırı çalıştır"""
        line = line.strip()
        
        # Boş satırlar
        if not line:
            return True
        
        # Yaz komutu
        if line.startswith('yaz '):
            parts = line[4:].strip()
            # Birden çok argüman için
            output = self.get_string_value(parts)
            print(output)
            return True
        
        # Yazır komutu (satır sonu olmadan)
        if line.startswith('yazır '):
            parts = line[6:].strip()
            output = self.get_string_value(parts)
            sys.stdout.write(output)
            sys.stdout.flush()
            return True
        
        # Oku komutu
        if line.startswith('oku '):
            var_name = line[4:].strip()
            try:
                value = input()
                try:
                    self.variables[var_name] = int(value)
                except ValueError:
                    try:
                        self.variables[var_name] = float(value)
                    except ValueError:
                        self.variables[var_name] = value
            except EOFError:
                self.variables[var_name] = ""
            return True
        
        # Oku dosya komutu
        if line.startswith('dosya_oku '):
            parts = line[11:].strip().split(' ')
            if len(parts) >= 2:
                dosya = self.get_string_value(parts[0])
                var_name = parts[1]
                try:
                    with open(dosya, 'r', encoding='utf-8') as f:
                        self.variables[var_name] = f.read()
                except Exception as e:
                    print(f"Hata: Dosya okunamadı - {e}")
            return True
        
        # Yaz dosya komutu
        if line.startswith('dosya_yaz '):
            parts = line[11:].strip().split(' ')
            if len(parts) >= 2:
                dosya = self.get_string_value(parts[0])
                içerik = self.get_string_value(parts[1])
                try:
                    with open(dosya, 'w', encoding='utf-8') as f:
                        f.write(içerik)
                except Exception as e:
                    print(f"Hata: Dosya yazılamadı - {e}")
            return True
        
        # Dizi oluştur
        if line.startswith('dizi '):
            parts = line[5:].strip().split('=')
            if len(parts) == 2:
                var_name = parts[0].strip()
                # Dizi değerleri
                values_str = parts[1].strip()
                if values_str.startswith('[') and values_str.endswith(']'):
                    values_str = values_str[1:-1]
                    items = [self.evaluate_expression(item.strip()) for item in values_str.split(',')]
                    self.variables[var_name] = items
                else:
                    # Boş dizi
                    self.variables[var_name] = []
            return True
        
        # Dizi ekle
        if line.startswith('ekle '):
            parts = line[5:].strip().split(' ')
            if len(parts) >= 2:
                array_name = parts[0]
                value = self.evaluate_expression(' '.join(parts[1:]))
                if array_name in self.variables and isinstance(self.variables[array_name], list):
                    self.variables[array_name].append(value)
            return True
        
        # Dizi sil
        if line.startswith('sil '):
            parts = line[4:].strip()
            match = re.match(r'(\w+)\[(\d+)\]', parts)
            if match:
                array_name = match.group(1)
                index = int(match.group(2))
                if array_name in self.variables and isinstance(self.variables[array_name], list):
                    if 0 <= index < len(self.variables[array_name]):
                        self.variables[array_name].pop(index)
            return True
        
        # Dizi uzunluğu
        if line.startswith('uzunluk '):
            parts = line[8:].strip().split('=')
            if len(parts) == 2:
                result_var = parts[0].strip()
                array_name = parts[1].strip()
                if array_name in self.variables:
                    if isinstance(self.variables[array_name], (list, str)):
                        self.variables[result_var] = len(self.variables[array_name])
            return True
        
        # Dön komutu (return)
        if line.startswith('dön '):
            self.return_value = self.evaluate_expression(line[4:].strip())
            self.break_flag = True
            return True
        
        # Kes komutu (break)
        if line == 'kes':
            self.break_flag = True
            return True
        
        # Devam komutu (continue)
        if line == 'devam':
            self.continue_flag = True
            return True
        
        # Atama (x = 5, name = "Ali")
        if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=', '≠', '≤', '≥']):
            parts = line.split('=', 1)
            var_name = parts[0].strip()
            value = self.evaluate_expression(parts[1].strip())
            self.variables[var_name] = value
            return True
        
        # Fonksiyon çağırı
        if line.startswith('çağır '):
            func_name = line[6:].strip().rstrip('()')
            self.call_function(func_name)
            return True
        
        return True

    def call_function(self, func_name: str):
        """Fonksiyon çağır"""
        if func_name not in self.functions:
            print(f"Hata: {func_name} fonksiyonu tanımlanmadı")
            return
        
        self.in_function = True
        self.return_value = None
        old_line = self.current_line
        
        # Fonksiyon satırlarını bul
        func_start = None
        for i, line in enumerate(self.lines):
            if line.startswith(f'fonk {func_name}'):
                func_start = i + 1
                break
        
        if func_start is None:
            self.in_function = False
            return
        
        # Fonksiyon içindeki satırları çalıştır
        func_end = func_start
        for i in range(func_start, len(self.lines)):
            if self.lines[i] == 'bitir':
                func_end = i
                break
        
        self.current_line = func_start
        while self.current_line < func_end:
            if self.break_flag:
                break
            self.execute_line(self.lines[self.current_line])
            self.current_line += 1
        
        self.break_flag = False
        self.in_function = False
        self.current_line = old_line

    def run(self, code: str):
        """Kodu çalıştır"""
        self.lines = self.tokenize(code)
        self.current_line = 0
        
        try:
            while self.current_line < len(self.lines):
                line = self.lines[self.current_line]
                
                if self.break_flag:
                    break
                if self.continue_flag:
                    self.continue_flag = False
                    self.current_line += 1
                    continue
                
                # Eğer-bitir bloku
                if line.startswith('eğer '):
                    condition = line[5:].strip()
                    if condition.endswith(' ise'):
                        condition = condition[:-4]
                    
                    condition_result = self.evaluate_expression(condition)
                    
                    if condition_result:
                        self.current_line += 1
                        while self.current_line < len(self.lines) and self.lines[self.current_line] != 'bitir':
                            if self.break_flag or self.continue_flag:
                                break
                            self.execute_line(self.lines[self.current_line])
                            self.current_line += 1
                    else:
                        self.current_line += 1
                        while self.current_line < len(self.lines) and self.lines[self.current_line] != 'bitir':
                            self.current_line += 1
                    
                    self.current_line += 1
                    continue
                
                # Tekrarla-bitir bloku (Sayı)
                elif line.startswith('tekrarla '):
                    match = re.match(r'tekrarla\s+(\d+)\s+kez', line)
                    if match:
                        times = int(match.group(1))
                        loop_start = self.current_line + 1
                        
                        # Loop sonunu bul
                        loop_end = loop_start
                        depth = 1
                        for i in range(loop_start, len(self.lines)):
                            if self.lines[i].startswith(('tekrarla', 'eğer', 'fonk')):
                                depth += 1
                            elif self.lines[i] == 'bitir':
                                depth -= 1
                                if depth == 0:
                                    loop_end = i
                                    break
                        
                        for _ in range(times):
                            if self.break_flag:
                                break
                            self.current_line = loop_start
                            while self.current_line < loop_end:
                                if self.break_flag:
                                    break
                                if self.continue_flag:
                                    self.continue_flag = False
                                    self.current_line += 1
                                    continue
                                self.execute_line(self.lines[self.current_line])
                                self.current_line += 1
                        
                        self.current_line = loop_end + 1
                        self.break_flag = False
                        continue
                
                # Fonksiyon tanımı
                elif line.startswith('fonk '):
                    func_name = line[5:].strip().rstrip('()')
                    self.functions[func_name] = True
                    # Fonksiyon tanımını atla
                    self.current_line += 1
                    while self.current_line < len(self.lines) and self.lines[self.current_line] != 'bitir':
                        self.current_line += 1
                    self.current_line += 1
                    continue
                
                else:
                    self.execute_line(line)
                
                self.current_line += 1
        
        except KeyboardInterrupt:
            print("\nProgram kullanıcı tarafından durduruldu.")
        except Exception as e:
            print(f"Hata: {e}")

def main():
    if len(sys.argv) < 2:
        print("╔════════════════════════════════════════╗")
        print("║   Türkçe Programlama Dili v1.0        ║")
        print("║   Tam Versiyon                         ║")
        print("╚════════════════════════════════════════╝")
        print("\nKullanım: python turkce.py program.tr")
        print("\nÖrnek çalıştırma:")
        print("  python turkce.py ornekler/merhaba.tr")
        print("  python turkce.py ornekler/hesapla.tr")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
        
        interpreter = TurkceInterpreter()
        interpreter.run(code)
    
    except FileNotFoundError:
        print(f"❌ Hata: '{sys.argv[1]}' dosyası bulunamadı")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
