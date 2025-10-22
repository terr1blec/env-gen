"""
ChEMBL Server Dataset Synthesis Module

Generates deterministic mock datasets for ChEMBL server testing.
"""

import json
import random


def generate_dataset(seed=42):
    """Generate a synthetic ChEMBL dataset with deterministic data."""
    random.seed(seed)
    
    # Generate unique IDs for different entity types
    compound_ids = ["CHEMBL1000", "CHEMBL1001"]
    assay_ids = ["CHEMBL2000", "CHEMBL2001"]
    target_ids = ["CHEMBL3000", "CHEMBL3001"]
    activity_ids = ["ACT0", "ACT1"]
    
    # Build the comprehensive dataset matching the data contract
    dataset = {
        "activity_data": [
            {
                "assay_chembl_id": assay_ids[0],
                "activity_data": [
                    {
                        "activity_id": activity_ids[0],
                        "molecule_chembl_id": compound_ids[0],
                        "standard_value": 10.5,
                        "standard_units": "nM",
                        "standard_type": "IC50",
                        "pchembl_value": 8.0
                    }
                ]
            }
        ],
        "supplementary_activity_data": [
            {
                "activity_chembl_id": activity_ids[0],
                "supplementary_data": [
                    {
                        "data_type": "kinetic_parameter",
                        "value": 5.0,
                        "units": "s⁻¹"
                    }
                ]
            }
        ],
        "assay_data": [
            {
                "assay_type": "B",
                "assay_data": [
                    {
                        "assay_chembl_id": assay_ids[0],
                        "assay_description": "Binding assay",
                        "assay_organism": "Homo sapiens",
                        "confidence_score": 7
                    }
                ]
            }
        ],
        "assay_class_data": [
            {
                "assay_class_type": "DISEASE-RELATED",
                "classification_data": [
                    {
                        "assay_class_id": "AC0",
                        "class_name": "Class 0",
                        "description": "Disease assay class"
                    }
                ]
            }
        ],
        "atc_class_data": [
            {
                "level1": "A",
                "atc_data": [
                    {
                        "atc_code": "A01B01",
                        "description": "Alimentary drug",
                        "drug_name": "Drug 1"
                    }
                ]
            }
        ],
        "binding_site_data": [
            {
                "site_name": "Active Site",
                "binding_data": [
                    {
                        "site_id": "BS0",
                        "description": "Binding site 0",
                        "residues": ["ALA", "VAL"]
                    }
                ]
            }
        ],
        "biotherapeutic_data": [
            {
                "biotherapeutic_type": "Monoclonal Antibody",
                "biotherapeutic_data": [
                    {
                        "biotherapeutic_id": "BIO0",
                        "name": "mAb-0",
                        "target": "Target Protein 0"
                    }
                ]
            }
        ],
        "cell_line_data": [
            {
                "cell_line_name": "HEK293",
                "cell_line_data": [
                    {
                        "cell_line_id": "CL0",
                        "description": "Human kidney cell line",
                        "tissue_type": "Kidney"
                    }
                ]
            }
        ],
        "chembl_id_lookup": [
            {
                "available_type": "compound",
                "q": "aspirin",
                "lookup_results": [
                    {
                        "chembl_id": compound_ids[0],
                        "name": "Aspirin",
                        "type": "compound"
                    }
                ]
            }
        ],
        "chembl_release_data": [
            {
                "release_data": [
                    {
                        "release_version": "ChEMBL_33",
                        "release_date": "2024-01-01",
                        "compounds_count": 2500000
                    }
                ]
            }
        ],
        "compound_records": [
            {
                "compound_name": "Aspirin",
                "records": [
                    {
                        "record_id": "REC0",
                        "chembl_id": compound_ids[0],
                        "molecular_formula": "C9H8O4",
                        "molecular_weight": 180.16
                    }
                ]
            }
        ],
        "compound_structural_alerts": [
            {
                "alert_name": "PAINS",
                "alerts": [
                    {
                        "alert_id": "ALERT0",
                        "description": "Pan-assay interference structure",
                        "smarts": "[#6]1[#6][#6][#6][#6][#6]1"
                    }
                ]
            }
        ],
        "description_data": [
            {
                "description_type": "assay",
                "descriptions": [
                    {
                        "description_id": "DESC0",
                        "text": "Assay description"
                    }
                ]
            }
        ],
        "document_data": [
            {
                "journal": "Journal of Medicinal Chemistry",
                "documents": [
                    {
                        "document_id": "DOC0",
                        "title": "Research paper",
                        "year": 2023
                    }
                ]
            }
        ],
        "drug_data": [
            {
                "drug_type": "Small Molecule",
                "drug_data": [
                    {
                        "drug_id": "DRUG0",
                        "name": "Drug Candidate 0",
                        "phase": "Phase I"
                    }
                ]
            }
        ],
        "drug_indication_data": [
            {
                "mesh_heading": "Pain",
                "indications": [
                    {
                        "indication_id": "IND0",
                        "drug_name": "Analgesic 0",
                        "condition": "Chronic pain"
                    }
                ]
            }
        ],
        "drug_warning_data": [
            {
                "meddra_term": "Hepatotoxicity",
                "warnings": [
                    {
                        "warning_id": "WARN0",
                        "drug_name": "Drug 0",
                        "severity": "Mild"
                    }
                ]
            }
        ],
        "go_slim_data": [
            {
                "go_slim_term": "molecular_function",
                "go_data": [
                    {
                        "go_id": "GO:0000001",
                        "name": "Molecular function 1",
                        "namespace": "molecular_function"
                    }
                ]
            }
        ],
        "mechanism_data": [
            {
                "mechanism_of_action": "Enzyme Inhibition",
                "mechanisms": [
                    {
                        "mechanism_id": "MECH0",
                        "target_name": "Target Enzyme 0",
                        "description": "Enzyme inhibition"
                    }
                ]
            }
        ],
        "molecule_data": [
            {
                "molecule_type": "Small molecule",
                "molecules": [
                    {
                        "molecule_chembl_id": compound_ids[0],
                        "pref_name": "Aspirin",
                        "max_phase": 4,
                        "molecular_weight": 180.16
                    }
                ]
            }
        ],
        "molecule_form_data": [
            {
                "form_description": "Salt form",
                "forms": [
                    {
                        "form_id": "FORM0",
                        "parent_chembl_id": compound_ids[0],
                        "description": "Salt form 0"
                    }
                ]
            }
        ],
        "organism_data": [
            {
                "tax_id": 9606,
                "organisms": [
                    {
                        "organism_id": "ORG0",
                        "scientific_name": "Homo sapiens",
                        "common_name": "Human"
                    }
                ]
            }
        ],
        "protein_classification_data": [
            {
                "protein_class_name": "Kinase",
                "classifications": [
                    {
                        "protein_class_id": "PC0",
                        "level": 1,
                        "description": "Protein kinase class"
                    }
                ]
            }
        ],
        "source_data": [
            {
                "source_description": "Scientific literature",
                "sources": [
                    {
                        "source_id": "SRC0",
                        "name": "Source 0",
                        "url": "https://example.com/source0"
                    }
                ]
            }
        ],
        "target_data": [
            {
                "target_type": "SINGLE PROTEIN",
                "targets": [
                    {
                        "target_chembl_id": target_ids[0],
                        "pref_name": "Target 0",
                        "organism": "Homo sapiens",
                        "target_type": "SINGLE PROTEIN"
                    }
                ]
            }
        ],
        "target_component_data": [
            {
                "component_type": "Protein",
                "components": [
                    {
                        "component_id": "COMP0",
                        "accession": "P00001",
                        "component_description": "Protein component 0"
                    }
                ]
            }
        ],
        "target_relation_data": [
            {
                "relationship_type": "Homology",
                "relations": [
                    {
                        "relation_id": "REL0",
                        "source_target": target_ids[0],
                        "target_target": target_ids[1],
                        "relationship": "Homologous"
                    }
                ]
            }
        ],
        "tissue_data": [
            {
                "tissue_name": "Liver",
                "tissues": [
                    {
                        "tissue_id": "TIS0",
                        "organism": "Homo sapiens",
                        "description": "Liver tissue"
                    }
                ]
            }
        ],
        "xref_source_data": [
            {
                "xref_name": "UniProt",
                "xrefs": [
                    {
                        "xref_id": "XREF0",
                        "accession": "P00001",
                        "source_db": "UniProt"
                    }
                ]
            }
        ],
        "chemistry_operations": [
            {
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "inchi": "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)",
                "fragment": "No",
                "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "inchi_key": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
                "svg_image": "<svg width=\"200\" height=\"200\"><text x=\"100\" y=\"100\">CC(=O)Oc1ccccc1C(=O)</text></svg>",
                "is_3d": False,
                "descriptors": {
                    "molecular_weight": 180.16,
                    "logp": 1.19,
                    "heavy_atom_count": 13
                },
                "structural_alerts": [
                    {
                        "alert_id": "ALERT1",
                        "name": "Ester",
                        "description": "Ester functional group"
                    }
                ]
            }
        ],
        "chembl_utils": [
            {
                "chembl_id": compound_ids[0],
                "description": "Utility description",
                "official_name": "Official Name",
                "parent_chembl_id": None
            }
        ],
        "status_data": {
            "status": {
                "service": "ChEMBL Web Services",
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00",
                "database": "ChEMBL_33",
                "compounds": 2500000,
                "assays": 15000,
                "targets": 12000
            }
        }
    }
    
    return dataset


def main():
    """Main function to generate and save the dataset."""
    import sys
    
    # Parse command line arguments
    seed = 42
    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid seed '{sys.argv[1]}', using default seed=42")
    
    # Generate dataset
    dataset = generate_dataset(seed=seed)
    
    # Save to the recommended path
    dataset_path = "generated\\chembl-server\\chembl_server_dataset.json"
    with open(dataset_path, "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Dataset generated successfully with seed={seed}!")
    print(f"Saved to: {dataset_path}")


if __name__ == "__main__":
    main()