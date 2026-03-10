(.venv) PS C:\Users\treyr\Documents\algorithmic_empire> & c:/Users/treyr/Documents/algorithmic_empire/.venv/Scripts/python.exe c:/Users/treyr/Documents/algorithmic_empire/ARCS/attribution_engine.py    
Attribution engine status: {
  "engine_status": "operational",
  "active_attributions": 0,
  "actor_profiles_created": 0,
  "attribution_hypotheses": 0,
  "campaign_correlations": 0,
  "metrics": {},
  "model_versions": {
    "actor_profiler": {
      "version": 1.0,
      "last_updated": "2026-02-16 14:48:42.683876+00:00",
      "training_samples": 0,
      "attribution_accuracy": 0.0,
      "false_positive_rate": 0.0
    },
    "campaign_correlator": {
      "version": 1.0,
      "last_updated": "2026-02-16 14:48:42.688939+00:00",
      "training_samples": 0,
      "attribution_accuracy": 0.0,
      "false_positive_rate": 0.0
    },
    "attribution_classifier": {
      "version": 1.0,
      "last_updated": "2026-02-16 14:48:42.693190+00:00",
      "training_samples": 0,
      "attribution_accuracy": 0.0,
      "false_positive_rate": 0.0
    },
    "confidence_estimator": {
      "version": 1.0,
      "last_updated": "2026-02-16 14:48:42.695480+00:00",
      "training_samples": 0,
      "attribution_accuracy": 0.0,
      "false_positive_rate": 0.0
    },
    "deception_detector": {
      "version": 1.0,
      "last_updated": "2026-02-16 14:48:42.699430+00:00",
      "training_samples": 0,
      "attribution_accuracy": 0.0,
      "false_positive_rate": 0.0
    }
  },
  "background_tasks_active": 4,
  "configuration": {
    "actor_profiling": {
      "behavioral_analysis_enabled": true,
      "infrastructure_analysis_enabled": true,
      "malware_genealogy_enabled": true,
      "temporal_analysis_enabled": true
    },
    "attribution": {
      "attribution_interval_hours": 6,
      "continuous_attribution_enabled": true,
      "max_concurrent_attributions": 5,
      "min_attribution_confidence": 0.6
    },
    "learning": {
      "learning_rate": 0.0015,
      "model_update_interval_hours": 0.75,
      "recursive_learning_enabled": true,
      "training_batch_size": 48
    },
    "validation": {
      "confidence_threshold_validation": 0.8,
      "hypothesis_validation_enabled": true,
      "peer_review_required": false
    }
  },
  "last_updated": "2026-02-16T14:48:42.703843+00:00"
}
Attribution engine test completed successfully