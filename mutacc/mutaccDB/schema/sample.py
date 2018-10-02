SAMPLE_VALIDATOR = {
        
        "$jsonSchema": {
            
            "bsonType": "object",

            "required": ["sample_id", "variants", "case", "sex", "analysis_type", "bam_file",
                "fastq_files", "variant_fastq_files"],

            "properties": {
                
                "sample_id": {
                    
                    "bsonType": "string",

                    },

                "variants": {
                    
                    "bsonType": "array",

                    "description": "array of of variant _id for variants in the sample",

                    "items": {
                        
                        "bsonType": "objectId"
                        
                        }
                    
                    },

                "case": {
                    
                    "bsonType": "string",

                    "description": "case_id for the case that this sample belongs to"

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

                        }

                }

            }
        
        }
