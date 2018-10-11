from .sample import SAMPLE_VALIDATOR

SAMPLE_OBJECT = SAMPLE_VALIDATOR["$jsonSchema"]

CASE_VALIDATOR = {
        
        "$jsonSchema": {
            
            "bsonType": "object",

            "required": ["case_id", "samples", "variants"],

            "properties": {

                "case_id": {
                    
                    "bsonType": "string"
                    
                    },

                "samples": {
                    
                    "bsonType": "array",

                    "description": "array of sample objects in the case",

                    "items": SAMPLE_OBJECT

                    },

                "variants": {
                    
                    "bsonType": "array",

                    "description": "array of variant _id for variants in the case",

                    "items": {

                        "bsonType": "objectId"
                        
                        }
                    
                    }
                
                }
            
            }
        
        }
