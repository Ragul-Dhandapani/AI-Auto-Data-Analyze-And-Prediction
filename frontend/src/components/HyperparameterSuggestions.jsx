import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Lightbulb, Copy, CheckCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const HyperparameterSuggestions = ({ suggestions }) => {
  const [copiedModel, setCopiedModel] = useState(null);

  if (!suggestions || Object.keys(suggestions).length === 0) {
    return null;
  }

  const copyToClipboard = (modelName, params) => {
    const text = JSON.stringify(params, null, 2);
    navigator.clipboard.writeText(text);
    setCopiedModel(modelName);
    toast.success(`Copied ${modelName} parameters!`);
    setTimeout(() => setCopiedModel(null), 2000);
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-300">
      <div className="flex items-center gap-3 mb-4">
        <Lightbulb className="w-6 h-6 text-yellow-600" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            🤖 AI-Powered Hyperparameter Tuning Suggestions
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Optimize your models with these AI-recommended parameters. Copy and use them in the "Hyperparameter Tuning" tab.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {Object.entries(suggestions).map(([modelName, suggestion]) => (
          <Card key={modelName} className="p-4 bg-white border border-yellow-200">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">{modelName}</h4>
                <p className="text-sm text-gray-600 mb-3">{suggestion.rationale}</p>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => copyToClipboard(modelName, suggestion.recommended || suggestion.parameters)}
                className="ml-3"
              >
                {copiedModel === modelName ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-1 text-green-600" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-1" />
                    Copy
                  </>
                )}
              </Button>
            </div>

            {suggestion.recommended && (
              <div className="mb-3 p-3 bg-green-50 rounded border border-green-200">
                <p className="text-xs font-semibold text-green-800 mb-2">
                  ⭐ Recommended Starting Point:
                </p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                  {Object.entries(suggestion.recommended).map(([param, value]) => (
                    <div key={param} className="flex items-center gap-1">
                      <span className="text-gray-600">{param}:</span>
                      <span className="font-mono font-semibold text-green-700">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {suggestion.parameters && (
              <div className="p-3 bg-gray-50 rounded border border-gray-200">
                <p className="text-xs font-semibold text-gray-700 mb-2">
                  Parameter Ranges to Explore:
                </p>
                <div className="space-y-1 text-sm">
                  {Object.entries(suggestion.parameters).map(([param, values]) => (
                    <div key={param} className="flex items-start gap-2">
                      <span className="text-gray-600 min-w-[140px]">{param}:</span>
                      <span className="font-mono text-gray-800">
                        {Array.isArray(values) ? values.join(', ') : String(values)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
        <p className="text-xs text-blue-800">
          💡 <strong>How to use:</strong> Copy the recommended parameters and paste them into the 
          "Hyperparameter Tuning" tab above. Run the tuning process to find the optimal combination 
          for your specific dataset.
        </p>
      </div>
    </Card>
  );
};

export default HyperparameterSuggestions;
