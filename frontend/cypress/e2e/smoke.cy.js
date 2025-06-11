// Cypress smoke test covering key flows
it('runs core flows without error', () => {
  cy.login();
  cy.visit('/assistants/onboarding');
  cy.contains('Create').click();
  cy.visit('/tour');
  cy.get('.react-joyride__tooltip button').contains('Next').click({ multiple: true });
  cy.visit('/assistants/demo');
  cy.contains('Demo Recap');
  cy.visit('/assistants/test-assistant/reflect');
  cy.contains('Save');
});
