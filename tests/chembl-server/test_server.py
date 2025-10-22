"""
Basic test for the ChEMBL server module.
"""

import json
import sys
import os

# Add the generated directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'generated', 'chembl-server'))

def test_dataset_loading():
    """Test that the dataset can be loaded correctly."""
    try:
        from chembl_server_server import load_dataset
        dataset = load_dataset()
        
        # Check that all required keys are present
        required_keys = [
            "activity_data", "supplementary_activity_data", "assay_data", 
            "assay_class_data", "atc_class_data", "binding_site_data",
            "biotherapeutic_data", "cell_line_data", "chembl_id_lookup",
            "chembl_release_data", "compound_records", "compound_structural_alerts",
            "description_data", "document_data", "drug_data", "drug_indication_data",
            "drug_warning_data", "go_slim_data", "mechanism_data", "molecule_data",
            "molecule_form_data", "organism_data", "protein_classification_data",
            "source_data", "target_data", "target_component_data", "target_relation_data",
            "tissue_data", "xref_source_data", "chemistry_operations", "chembl_utils",
            "status_data"
        ]
        
        missing_keys = [key for key in required_keys if key not in dataset]
        assert len(missing_keys) == 0, f"Missing keys: {missing_keys}"
        
        print("✓ Dataset loading test passed")
        return True
        
    except Exception as e:
        print(f"✗ Dataset loading test failed: {e}")
        return False

def test_data_consistency():
    """Test that ChEMBL IDs are unique across entity types."""
    try:
        from chembl_server_server import load_dataset
        dataset = load_dataset()
        
        # Collect all ChEMBL IDs
        chembl_ids = set()
        
        # Check compound records
        for compound_group in dataset.get("compound_records", []):
            for record in compound_group.get("records", []):
                chembl_id = record.get("chembl_id")
                if chembl_id:
                    chembl_ids.add((chembl_id, "compound"))
        
        # Check assay data
        for assay_group in dataset.get("assay_data", []):
            for assay in assay_group.get("assay_data", []):
                chembl_id = assay.get("assay_chembl_id")
                if chembl_id:
                    chembl_ids.add((chembl_id, "assay"))
        
        # Check target data
        for target_group in dataset.get("target_data", []):
            for target in target_group.get("targets", []):
                chembl_id = target.get("target_chembl_id")
                if chembl_id:
                    chembl_ids.add((chembl_id, "target"))
        
        # Check for duplicates
        chembl_id_counts = {}
        for chembl_id, entity_type in chembl_ids:
            if chembl_id not in chembl_id_counts:
                chembl_id_counts[chembl_id] = []
            chembl_id_counts[chembl_id].append(entity_type)
        
        duplicates = {chembl_id: types for chembl_id, types in chembl_id_counts.items() if len(types) > 1}
        
        if duplicates:
            print(f"✗ Found duplicate ChEMBL IDs: {duplicates}")
            return False
        
        print("✓ Data consistency test passed")
        return True
        
    except Exception as e:
        print(f"✗ Data consistency test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running ChEMBL server tests...")
    
    test1_passed = test_dataset_loading()
    test2_passed = test_data_consistency()
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)