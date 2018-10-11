SAMPLE_VALIDATOR = {
        
        "$jsonSchema": {
            
            "bsonType": "object",

            "required": ["sample_id", "sex", "analysis_type", "bam_file"],

            "properties": {
                
                "sample_id": {
                    
                    "bsonType": "string",

                    },

                "sex": {
                    
                    "bsonType": "string"
                    
                    },

                "analysis_type": {
                    
                    "bsonType": "string"
                    
                    },

                "bam_file": {
                    
                    "bsonType": "string",

                    "description": "path to sample bam file"
                    
                    },

                "fastq_files": {
                        
                        "bsonType": "array",

                        "description": "array of paths to fastq_files of sample",

                        "items": {

                            "bsonType": "string"
                            
                            }
                        
                        },

                "variant_fastq_files": {
                        
                        "bsonType": "array",

                        "description": "array of paths to fastqfiles containing the reads that\
                        supports the variants in the sample",

                        "items": {
                            
                            "bsonType": "string"

                            }

                        },

                "variant_bam_file": {
                        
                        "bsonType": "string"
                        
                        }


                }

            }
        
        }
