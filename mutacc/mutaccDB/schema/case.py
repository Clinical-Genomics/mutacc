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

                    "description": "array of sample_id for all samples in the case",

                    "items": {

                        "bsonType": "string"

                        }
                    
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
