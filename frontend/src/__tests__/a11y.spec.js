import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'axe-core';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import OnboardingPage from '../pages/assistants/OnboardingPage';

describe('a11y', () => {
  it('onboarding page has no violations', async () => {
    const { container } = render(
      <I18nextProvider i18n={i18n}>
        <OnboardingPage />
      </I18nextProvider>
    );
    const results = await axe(container);
    expect(results.violations.length).toBe(0);
  });
});
