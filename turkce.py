#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türkçe Programlama Dili Yorumlayıcısı (Interpreter)
Version: 0.1 (Prototip)
"""

import sys
import re
from typing import Dict, List, Any, Tuple

class TurkceInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, List[str]] = {}
        self.lines: List[str] = []
        self.current_line: int = 0

    def tokenize(self, code: str) -> List[str]:
        """Kodu satırlara böl ve işle"""
        lines = code.strip().split('\n')
        return [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

    def evaluate_expression(self, expr: str) -> Any:
        """Matematiksel ve string ifadeleri değerlendir"""
        expr = expr.strip()
        
        # String kontrol
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
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
        
        # Matematiksel işlem
        try:
            # Güvenli eval (basit işlemler)
            for var_name, var_value in self.variables.items():
                expr = expr.replace(var_name, str(var_value))
            
            # Türkçe operatörler
            expr = expr.replace('ve', 'and')
            expr = expr.replace('veya', 'or')
            expr = expr.replace('değil', 'not')
            
            result = eval(expr)
            return result
        except:
            return expr

    def execute_line(self, line: str) -> bool:
        """Tek bir satırı çalıştır"""
        line = line.strip()
        
        # Yaz komutu
        if line.startswith('yaz '):
            text = line[4:].strip()
            text = text.strip('"').strip("'")
            # Değişkenleri değiştir
            for var_name, var_value in self.variables.items():
                text = text.replace(f'${var_name}', str(var_value))
            print(text)
            return True
        
        # Oku komutu
        if line.startswith('oku '):
            var_name = line[4:].strip()
            try:
                value = input()
                try:
                    self.variables[var_name] = int(value)
                except:
                    try:
                        self.variables[var_name] = float(value)
                    except:
                        self.variables[var_name] = value
            except EOFError:
                self.variables[var_name] = ""
            return True
        
        # Atama (x = 5, name = "Ali")
        if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
            parts = line.split('=', 1)
            var_name = parts[0].strip()
            value = self.evaluate_expression(parts[1].strip())
            self.variables[var_name] = value
            return True
        
        # Fonksiyon tanımı
        if line.startswith('fonk '):
            func_name = line[4:].strip().rstrip('():')
            self.functions[func_name] = []
            return True
        
        return True

    def run(self, code: str):
        """Kodu çalıştır"""
        self.lines = self.tokenize(code)
        self.current_line = 0
        
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            
            # Eğer-bitir bloku
            if line.startswith('eğer '):
                condition = line[5:].strip().rstrip(':').rstrip('ise')
                condition_result = self.evaluate_expression(condition)
                
                if condition_result:
                    self.current_line += 1
                    while self.current_line < len(self.lines) and self.lines[self.current_line] != 'bitir':
                        self.execute_line(self.lines[self.current_line])
                        self.current_line += 1
                else:
                    self.current_line += 1
                    while self.current_line < len(self.lines) and self.lines[self.current_line] != 'bitir':
                        self.current_line += 1
            
            # Tekrarla-bitir bloku
            elif line.startswith('tekrarla '):
                match = re.match(r'tekrarla\s+(\d+)\s+kez', line)
                if match:
                    times = int(match.group(1))
                    loop_start = self.current_line + 1
                    self.current_line += 1
                    
                    loop_end = self.current_line
                    while loop_end < len(self.lines) and self.lines[loop_end] != 'bitir':
                        loop_end += 1
                    
                    for _ in range(times):
                        self.current_line = loop_start
                        while self.current_line < loop_end:
                            self.execute_line(self.lines[self.current_line])
                            self.current_line += 1
                    
                    self.current_line = loop_end + 1
                    continue
            
            else:
                self.execute_line(line)
            
            self.current_line += 1

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python turkce.py program.tr")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
        
        interpreter = TurkceInterpreter()
        interpreter.run(code)
    
    except FileNotFoundError:
        print(f"Hata: {sys.argv[1]} dosyası bulunamadı")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
