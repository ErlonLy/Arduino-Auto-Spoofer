import json
import os

class SpoofEngine:
    def __init__(self):
        self.profiles_file = "mouse_profiles/profiles.json"
        self.load_profiles()
    
    def load_profiles(self):
        """Carrega os perfis de mouse"""
        default_profiles = {
            "Logitech": {
                "G502": {
                    "vid": "0x046D", 
                    "pid": "0xC08B",
                    "vendor": "Logitech",
                    "product": "G502 HERO",
                    "description": "Logitech G502 HERO Gaming Mouse"
                },
                "G903": {
                    "vid": "0x046D", 
                    "pid": "0xC087",
                    "vendor": "Logitech",
                    "product": "G903 LIGHTSPEED",
                    "description": "Logitech G903 Wireless Gaming Mouse"
                }
            },
            "Razer": {
                "DeathAdder V2": {
                    "vid": "0x1532", 
                    "pid": "0x0067",
                    "vendor": "Razer",
                    "product": "DeathAdder V2",
                    "description": "Razer DeathAdder V2 Gaming Mouse"
                }
            }
        }
        
        os.makedirs("mouse_profiles", exist_ok=True)
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'w') as f:
                json.dump(default_profiles, f, indent=2)
        
        with open(self.profiles_file, 'r') as f:
            return json.load(f)
    
    def get_profile(self, brand, model):
        """Obtém perfil específico do mouse"""
        profiles = self.load_profiles()
        return profiles.get(brand, {}).get(model, {})
    
    def add_profile(self, brand, model, profile_data):
        """Adiciona novo perfil"""
        profiles = self.load_profiles()
        
        if brand not in profiles:
            profiles[brand] = {}
        
        profiles[brand][model] = profile_data
        
        with open(self.profiles_file, 'w') as f:
            json.dump(profiles, f, indent=2)