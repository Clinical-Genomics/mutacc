VARIANT_VALIDATOR = {

        "$jsonSchema": {

            "bsonType": "object",

            "required": ["display_name", "variant_type", "alt", "ref", "chrom", "start", "end", "vcf_entry", "samples",

                "case", "reads_region"],

            "properties": {

                "display_name": {
                    
                    "bsonType": "string"

                    },

                "variant_type": {
                    
                    "bsonType": "string"

                    },

                "alt": {
                    
                    "bsonType": "array",

                    "items": {
                        
                        "bsonType": "string"
                        
                        }

                    },
               
                "ref": {

                    "bsonType": "string"    

                    },

                "chrom": {
                    
                    "bsonType": "string" 
                    
                    },

                "start": {

                    "bsonType": "int",

                    "description": "Start position for variant"

                    },

                "end": {
                    
                    "bsonType": "int",

                    "description": "End position for variant"
                    
                    },

                "vcf_entry": {
                    
                    "bsonType": "string",

                    "description": "Full vcf entry for variant"
                    
                    },

                "samples": {
                    
                    "bsonType": "array",

                    "description": "Samples from case",

                    "items": {
                        
                        "bsonType": "object",

                        "required": ["sample_id", "genotype"],

                        "properties": {
                            
                            "sample_id": {
                                
                                "bsonType": "string"

                                },
                            
                            "genotype": {
                                
                                "bsonType": "string"
                                
                                }
                             
                            }

                        }
                        
                    },

                "case": {
                       
                    "bsonType": "string"
                        
                    },

                "reads_region": {
                        
                        "bsonType": "object",

                        "required": ["start", "end"],

                        "properties": {
                        
                            "start": {
                                
                                "bsonType": "int"
                                
                            },

                            "end": {
                                
                                "bsonType": "int"    
                                
                            } 

                        }
                        
                    }

                }

            }
            
        }




   

    
