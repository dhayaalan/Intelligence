import React, { useState } from 'react';
import { Dialog } from '../../components/ui/Dialog';
import { Button } from '../../components/ui/Button';
import { useCases } from '../../core/api/hooks';
import { useAddToCaseNewsInvestigation } from '../../core/api/newsHooks';
import { Briefcase, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface AddToCaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  investigationId: string;
  investigationTitle: string;
}

export const AddToCaseModal: React.FC<AddToCaseModalProps> = ({
  isOpen,
  onClose,
  investigationId,
  investigationTitle,
}) => {
  const { data: cases = [], isLoading: isLoadingCases } = useCases();
  const addToCaseMutation = useAddToCaseNewsInvestigation();
  const [selectedCaseId, setSelectedCaseId] = useState<string>('');
  const [analystNotes, setAnalystNotes] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCaseId) return;

    try {
      await addToCaseMutation.mutateAsync({
        investigationId,
        caseId: selectedCaseId,
        analystNotes: analystNotes.trim() || undefined,
      });
      setSuccessMsg(`Successfully attached news investigation and evidence to case.`);
      setTimeout(() => {
        setSuccessMsg(null);
        onClose();
      }, 1500);
    } catch (err: any) {
      console.error('Failed to attach to case', err);
    }
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Attach Investigation to Case"
      description={`Link '${investigationTitle}' and its correlated evidence to an existing case file.`}
      maxWidth="max-w-md"
    >
      {successMsg ? (
        <div className="py-6 flex flex-col items-center justify-center text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center mb-3">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{successMsg}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
              Select Target Case File
            </label>
            {isLoadingCases ? (
              <div className="flex items-center space-x-2 py-3 text-xs text-slate-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Loading available cases...</span>
              </div>
            ) : cases.length === 0 ? (
              <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>No active cases found. Create a case in Case Management first to link news evidence.</span>
              </div>
            ) : (
              <select
                value={selectedCaseId}
                onChange={(e) => setSelectedCaseId(e.target.value)}
                required
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">-- Choose a Case --</option>
                {cases.map((c: any) => (
                  <option key={c.id} value={c.id}>
                    {c.title || c.target || c.id} ({c.status || 'ACTIVE'})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
              Analyst Notes & Justification
            </label>
            <textarea
              value={analystNotes}
              onChange={(e) => setAnalystNotes(e.target.value)}
              placeholder="Explain how this news intelligence connects to the case hypothesis..."
              rows={3}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
            />
          </div>

          {addToCaseMutation.isError && (
            <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs">
              {(addToCaseMutation.error as any)?.message || 'Failed to link investigation to case'}
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-200 dark:border-slate-800">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="default"
              size="sm"
              disabled={!selectedCaseId || addToCaseMutation.isPending}
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              {addToCaseMutation.isPending ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                  Linking...
                </>
              ) : (
                <>
                  <Briefcase className="w-3.5 h-3.5 mr-1.5" />
                  Link to Case
                </>
              )}
            </Button>
          </div>
        </form>
      )}
    </Dialog>
  );
};
