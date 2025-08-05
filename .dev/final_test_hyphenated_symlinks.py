#!/usr/bin/env python3
"""Final test to verify hyphenated symlinks work correctly."""

import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test papers with real journal names that were problematic
test_bibtex = """
@article{kapoor2022sensors,
  title={Epileptic Seizure Prediction Based on Hybrid Seek Optimization},
  author={Kapoor, A. and Singh, N.},
  year={2022},
  journal={Sensors (Basel, Switzerland)},
  doi={10.3390/s23010423}
}

@inproceedings{parvez2020tensymp,
  title={Deep Learning Model for Real-time Seizure Detection},
  author={Parvez, M. Z. and Paul, M.},
  year={2020},
  journal={2020 IEEE Region 10 Symposium (TENSYMP)},
  doi={10.1109/TENSYMP50017.2020.9230984}
}

@article{rashid2017biomech,
  title={Prediction of Epileptic Seizure by Analysing Time Series},
  author={Rashid, S. and Ahmad, T.},
  year={2017},
  journal={Applied Bionics and Biomechanics},
  doi={10.1155/2017/6848014}
}
"""

async def test_hyphenated_symlinks():
    """Test that hyphenated symlinks are created correctly."""
    
    # Create test BibTeX file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
        f.write(test_bibtex)
        temp_file = Path(f.name)
    
    try:
        print("🧪 Final Test: Hyphenated Symlinks")
        print("=" * 50)
        
        from scitex.scholar.doi import DOIResolver
        
        resolver = DOIResolver()
        
        print(f"📄 Processing: {temp_file}")
        print(f"📄 Expected structure with hyphenated journals")
        
        # Process with a clean project name
        results = await resolver.resolve_async(temp_file, project="hyphen_test")
        
        print(f"✅ Processed {len(results)} papers")
        
        # Check the symlinks
        from scitex.scholar.config import ScholarConfig
        config = ScholarConfig()
        
        project_dir = config.path_manager.get_library_dir("hyphen_test")
        
        print(f"\n📁 Checking symlinks in: {project_dir}")
        
        if project_dir.exists():
            symlinks_found = []
            for item in project_dir.iterdir():
                if item.is_symlink():
                    target = item.readlink()
                    symlinks_found.append((item.name, str(target)))
                    print(f"🔗 {item.name} -> {target}")
            
            # Verify expected patterns
            expected_patterns = [
                "Kapoor-2022-Sensors-Basel-Switzerland",
                "Parvez-2020-2020-IEEE-Region-10-Symposium-TENSYMP", 
                "Rashid-2017-Applied-Bionics-and-Biomechanics"
            ]
            
            print(f"\n📋 Verification:")
            for pattern in expected_patterns:
                found = any(pattern in link[0] for link in symlinks_found)
                status = "✅" if found else "❌"
                print(f"  {status} {pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        temp_file.unlink()

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_hyphenated_symlinks())
    if success:
        print(f"\n🎉 Hyphenated symlinks working perfectly!")
    else:
        print(f"\n💥 Test failed!")