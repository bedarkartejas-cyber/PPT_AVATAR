'use client';

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type OnboardingStep = 'info' | 'complete';

export function OnboardingForm() {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('info');
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    department: '',
    jobTitle: '',
    startDate: '',
  });

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const goToStep = (step: OnboardingStep) => {
    setCurrentStep(step);
  };

  // Expose navigation function globally for AI control
  useEffect(() => {
    (window as unknown as { goToStep: typeof goToStep }).goToStep = goToStep;
    return () => {
      delete (window as unknown as { goToStep?: typeof goToStep }).goToStep;
    };
  }, []);

  const steps: { id: OnboardingStep; label: string; number: number }[] = [
    { id: 'info', label: 'Your Information', number: 1 },
    { id: 'complete', label: 'Complete', number: 2 },
  ];

  return (
    <div className="mx-auto min-h-screen w-full max-w-4xl bg-white px-6 py-12">
      {/* Header */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900">Employee Onboarding</h1>
        <p className="mt-2 text-lg text-gray-600">
          Welcome! Please complete your onboarding information
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-12 flex items-center justify-center space-x-4">
        {steps.map((step, idx) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  'flex h-12 w-12 items-center justify-center rounded-full border-2 font-semibold transition-all',
                  currentStep === step.id
                    ? 'border-blue-500 bg-blue-500 text-white'
                    : steps.findIndex((s) => s.id === currentStep) > idx
                      ? 'border-green-500 bg-green-500 text-white'
                      : 'border-gray-300 bg-white text-gray-400'
                )}
              >
                {steps.findIndex((s) => s.id === currentStep) > idx ? '✓' : step.number}
              </div>
              <span
                className={cn(
                  'mt-2 text-sm',
                  currentStep === step.id ? 'font-semibold text-blue-500' : 'text-gray-500'
                )}
              >
                {step.label}
              </span>
            </div>
            {idx < steps.length - 1 && (
              <div
                className={cn(
                  'mx-4 h-0.5 w-24',
                  steps.findIndex((s) => s.id === currentStep) > idx
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Form Content */}
      <div className="rounded-lg border border-gray-200 bg-white p-8 shadow-sm">
        {currentStep === 'info' && (
          <div className="space-y-6">
            <h2 className="mb-6 text-2xl font-semibold text-gray-900">Your Information</h2>

            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <label htmlFor="fullName" className="mb-2 block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <input
                  type="text"
                  name="fullName"
                  id="fullName"
                  value={formData.fullName}
                  onChange={(e) => updateField('fullName', e.target.value)}
                  readOnly
                  className="w-full cursor-not-allowed rounded-md border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="email" className="mb-2 block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  readOnly
                  className="w-full cursor-not-allowed rounded-md border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="phone" className="mb-2 block text-sm font-medium text-gray-700">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => updateField('phone', e.target.value)}
                  readOnly
                  className="w-full cursor-not-allowed rounded-md border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label
                  htmlFor="department"
                  className="mb-2 block text-sm font-medium text-gray-700"
                >
                  Department
                </label>
                <input
                  type="text"
                  name="department"
                  id="department"
                  value={formData.department}
                  onChange={(e) => updateField('department', e.target.value)}
                  readOnly
                  className="w-full cursor-not-allowed rounded-md border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="jobTitle" className="mb-2 block text-sm font-medium text-gray-700">
                  Job Title
                </label>
                <input
                  type="text"
                  name="jobTitle"
                  id="jobTitle"
                  value={formData.jobTitle}
                  onChange={(e) => updateField('jobTitle', e.target.value)}
                  readOnly
                  className="w-full cursor-not-allowed rounded-md border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="startDate" className="mb-2 block text-sm font-medium text-gray-700">
                  Start Date
                </label>
                <input
                  type="text"
                  name="startDate"
                  id="startDate"
                  value={formData.startDate}
                  onChange={(e) => updateField('startDate', e.target.value)}
                  readOnly
                  className="w-full cursor-not-allowed rounded-md border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <Button
                id="nav-complete"
                data-nav="complete"
                onClick={() => goToStep('complete')}
                variant="primary"
                size="lg"
                className="pointer-events-none opacity-80"
              >
                Submit
              </Button>
            </div>
          </div>
        )}

        {currentStep === 'complete' && (
          <div className="py-12 text-center">
            <div className="mb-6 text-6xl">✅</div>
            <h2 className="mb-4 text-3xl font-semibold text-gray-900">Onboarding Complete!</h2>
            <p className="mb-8 text-lg text-gray-700">
              Thank you for completing your onboarding information.
            </p>
            <p className="mb-8 text-gray-600">
              Your information has been submitted to HR. You&apos;ll receive a confirmation email
              shortly.
            </p>
            <Button
              id="nav-info-restart"
              data-nav="info"
              onClick={() => goToStep('info')}
              variant="outline"
              size="lg"
              className="pointer-events-none opacity-80"
            >
              Start Over
            </Button>
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="mt-8 rounded-lg border border-blue-200 bg-blue-50 p-6">
        <h3 className="mb-2 font-semibold text-blue-900">🤖 AI-Assisted Form</h3>
        <p className="text-sm text-blue-800">
          This form is controlled by Maya, our AI assistant. Just tell her your information and
          she&apos;ll fill it in for you. The form fields are read-only to ensure accuracy.
        </p>
      </div>
    </div>
  );
}
