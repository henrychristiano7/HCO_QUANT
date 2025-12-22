"""
HCO-Quant: Jaseci Client Entry Point
"""

# Import symbols directly from the Jac module
import from backend.src.jac.main { AssetOrchestrator, SecurityScanner }

# --- 1. Client Orchestration Walker ---
walker hco_client {
    has symbols: str = "AAPL,TSLA,GOOG";
    has test_url: str = "http://example.com";
    has mock_mode: bool = True;

    can run_demo with `root entry {
        print("--- 🚀 HCO-QUANT JASECI CLIENT STARTING ---");
        
        print(f"Phase 1: Spawning AssetOrchestrator for {self.symbols}...");
        
        # FIX: Explicitly instantiate the walker and then spawn it on 'here'
        # This prevents the 'Root object is not callable' error inside the walker
        AssetOrchestrator(
            symbols = self.symbols, 
            mock = self.mock_mode
        ) spawn here;

        print("Phase 1 Complete. Results received from Jaseci Graph.");
        
        print(f"Phase 2: Spawning SecurityScanner for {self.test_url}...");
        
        # FIX: Explicitly instantiate SecurityScanner
        SecurityScanner(url = self.test_url) spawn here;

        report {
            "client_status": "Successful",
            "assets_processed": self.symbols,
            "security_check": "Complete",
            "jaseci_version": "0.9.x"
        };
        
        print("--- ✅ DEMO COMPLETE ---");
    }
}

# --- 2. Execution Entry Point ---
with entry {
    # Using the 'instance spawn node' syntax for maximum stability
    hco_client() spawn root;
}
