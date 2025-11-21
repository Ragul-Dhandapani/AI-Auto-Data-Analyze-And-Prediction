// MongoDB Initialization Script
// Run with: mongosh test_database /app/init_mongodb.js

print("🚀 Initializing PROMISE AI MongoDB Database...\n");

// Create collections if they don't exist
db.createCollection("workspaces");
db.createCollection("datasets");
db.createCollection("training_metadata");
db.createCollection("saved_states");
db.createCollection("prediction_feedback");

print("✅ Collections created\n");

// Create indexes for workspaces
print("Creating indexes for workspaces...");
db.workspaces.createIndex({ id: 1 }, { unique: true });
db.workspaces.createIndex({ created_at: -1 });
db.workspaces.createIndex({ name: 1 });

// Create indexes for datasets
print("Creating indexes for datasets...");
db.datasets.createIndex({ id: 1 }, { unique: true });
db.datasets.createIndex({ workspace_id: 1 });
db.datasets.createIndex({ created_at: -1 });
db.datasets.createIndex({ name: 1 });

// Create indexes for training_metadata
print("Creating indexes for training_metadata...");
db.training_metadata.createIndex({ dataset_id: 1 });
db.training_metadata.createIndex({ workspace_id: 1 });
db.training_metadata.createIndex({ timestamp: -1 });
db.training_metadata.createIndex({ model_type: 1 });
db.training_metadata.createIndex({ workspace_id: 1, timestamp: -1 });

// Create indexes for saved_states
print("Creating indexes for saved_states...");
db.saved_states.createIndex({ id: 1 }, { unique: true });
db.saved_states.createIndex({ dataset_id: 1 });
db.saved_states.createIndex({ workspace_name: 1 });
db.saved_states.createIndex({ created_at: -1 });

// Create indexes for prediction_feedback
print("Creating indexes for prediction_feedback...");
db.prediction_feedback.createIndex({ id: 1 }, { unique: true });
db.prediction_feedback.createIndex({ dataset_id: 1 });
db.prediction_feedback.createIndex({ created_at: -1 });

print("\n✅ All indexes created successfully!");

// Display collection stats
print("\n📊 Collection Statistics:");
print("  - Workspaces: " + db.workspaces.countDocuments({}));
print("  - Datasets: " + db.datasets.countDocuments({}));
print("  - Training Metadata: " + db.training_metadata.countDocuments({}));
print("  - Saved States: " + db.saved_states.countDocuments({}));
print("  - Prediction Feedback: " + db.prediction_feedback.countDocuments({}));

print("\n🎉 MongoDB initialization complete!");
