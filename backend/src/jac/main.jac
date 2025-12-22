"""HCO-Quant: Jaseci Orchestration Module."""

# 1. Native Import of Python modules/bridges
import src.pipelines.quant_async_pipeline as quant_pipe;
import src.agents.ai_agent as ai;
import src.agents.threat_intel_agent as security;

# --- 2. Graph Architecture ---
obj Asset {
    has symbol: str;
    has signal: str;
    has ai_comment: str;
}

# --- 3. Orchestration Walkers ---

walker AssetOrchestrator {
    has symbols: str;
    has mock: bool = True;
    has include_commentary: bool = True;

    can run_analysis with `root entry {
        results = []; 
        symbol_list = self.symbols.split(",");
        
        for sym in symbol_list {
            symbol_clean = sym.strip().upper();
            print(f"Jac-Agent: Processing {symbol_clean}");

            data = quant_pipe.process_asset_sync(
                symbol=symbol_clean,
                use_mock_data=self.mock,
                include_commentary=self.include_commentary
            );

            asset_record = Asset(
                symbol = symbol_clean,
                signal = data.get("action", "HOLD"),
                ai_comment = data.get("llm_commentary", "")
            );
            
            here ++> asset_record;
            results.append(data);
        }
        report results;
    }
}

# NEW: Added SecurityScanner walker to fix the FastAPI Import Error
walker SecurityScanner {
    has url: str;
    
    can run_scan with `root entry {
        print(f"Jac-Agent: Scanning {self.url}");
        # Calls the security sync bridge (Pattern 4)
        report quant_pipe.get_vt_report_sync(self.url);
    }
}

# --- 4. Utility Functions ---
def get_security_intel(target_url: str) -> dict {
    return quant_pipe.get_vt_report_sync(target_url);
}
