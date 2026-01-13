
import math

class PlayfairCipher:
    def __init__(self, key: str):
        self.key = key
        self.matrix = self._create_matrix(key)

    def _create_matrix(self, key):
        key = key.replace(" ", "").upper().replace("J", "I")
        seen = set()
        matrix = []
        
        # Add key first
        for char in key:
            if char not in seen and char.isalpha():
                seen.add(char)
                matrix.append(char)
        
        # Add remaining alphabet
        for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            if char not in seen:
                seen.add(char)
                matrix.append(char)
                
        return [matrix[i:i+5] for i in range(0, 25, 5)]

    def _find_position(self, char):
        for r, row in enumerate(self.matrix):
            if char in row:
                return r, row.index(char)
        return None

    def encrypt(self, plain_text):
        print("encrypting",plain_text)
        plain_text = plain_text.upper().replace("J", "I").replace(" ", "")
        digraphs = []
        i = 0
        while i < len(plain_text):
            a = plain_text[i]
            if i + 1 < len(plain_text):
                b = plain_text[i+1]
                if a == b:
                    digraphs.append((a, 'X'))
                    i += 1
                else:
                    digraphs.append((a, b))
                    i += 2
            else:
                digraphs.append((a, 'X'))
                i += 1

        cipher_text = ""
        for a, b in digraphs:
            r1, c1 = self._find_position(a)
            r2, c2 = self._find_position(b)

            if r1 == r2: # Same row
                cipher_text += self.matrix[r1][(c1 + 1) % 5]
                cipher_text += self.matrix[r2][(c2 + 1) % 5]
            elif c1 == c2: # Same column
                cipher_text += self.matrix[(r1 + 1) % 5][c1]
                cipher_text += self.matrix[(r2 + 1) % 5][c2]
            else: # Rectangle
                cipher_text += self.matrix[r1][c2]
                cipher_text += self.matrix[r2][c1]
        print("cipher text=",cipher_text)
        return cipher_text

    def decrypt(self, cipher_text):
        digraphs = []
        for i in range(0, len(cipher_text), 2):
            digraphs.append((cipher_text[i], cipher_text[i+1]))

        plain_text = ""
        for a, b in digraphs:
            r1, c1 = self._find_position(a)
            r2, c2 = self._find_position(b)

            if r1 == r2:
                plain_text += self.matrix[r1][(c1 - 1) % 5]
                plain_text += self.matrix[r2][(c2 - 1) % 5]
            elif c1 == c2:
                plain_text += self.matrix[(r1 - 1) % 5][c1]
                plain_text += self.matrix[(r2 - 1) % 5][c2]
            else:
                plain_text += self.matrix[r1][c2]
                plain_text += self.matrix[r2][c1]
        
        return plain_text


class RailFenceCipher:
    def __init__(self, rails: int):
        self.rails = int(rails)

    def encrypt(self, text):
        rail = [['\n' for i in range(len(text))]
                for j in range(self.rails)]
        
        dir_down = False
        row, col = 0, 0
        
        for i in range(len(text)):
            if (row == 0) or (row == self.rails - 1):
                dir_down = not dir_down
            
            rail[row][col] = text[i]
            col += 1
            
            if dir_down:
                row += 1
            else:
                row -= 1
        
        result = []
        for i in range(self.rails):
            for j in range(len(text)):
                if rail[i][j] != '\n':
                    result.append(rail[i][j])
        return("" . join(result))

    def decrypt(self, cipher):
        rail = [['\n' for i in range(len(cipher))]
                for j in range(self.rails)]
        
        dir_down = None
        row, col = 0, 0
        
        # Mark places
        for i in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == self.rails - 1:
                dir_down = False
            
            rail[row][col] = '*'
            col += 1
            
            if dir_down:
                row += 1
            else:
                row -= 1
        
        # Fill
        index = 0
        for i in range(self.rails):
            for j in range(len(cipher)):
                if ((rail[i][j] == '*') and (index < len(cipher))):
                    rail[i][j] = cipher[index]
                    index += 1
        
        # Read
        result = []
        row, col = 0, 0
        for i in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == self.rails - 1:
                dir_down = False
            
            # check the mark
            if rail[row][col] != '*':
                result.append(rail[row][col])
                col += 1
            
            if dir_down:
                row += 1
            else:
                row -= 1
        return("".join(result))

if __name__ == "__main__":
    # Simple Test
    pf = PlayfairCipher("MONARCHY")
    pt = "INSTRUMENTS"
    ct = pf.encrypt(pt)
    print(f"Playfair Encrypt '{pt}': {ct}")
    print(f"Playfair Decrypt: {pf.decrypt(ct)}")
    
    rf = RailFenceCipher(2)
    pt2 = "DEFENDTHEEASTWALL"
    ct2 = rf.encrypt(pt2)
    print(f"RailFence Encrypt '{pt2}': {ct2}")
    print(f"RailFence Decrypt: {rf.decrypt(ct2)}")
