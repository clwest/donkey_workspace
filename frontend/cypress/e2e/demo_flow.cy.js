// Cypress demo flow walk-through
it('runs through demo pages', () => {
  cy.login();
  cy.visit('/assistants-demos');
  cy.contains('Chat').first().click();
  cy.contains('Demo Recap').click();
  cy.contains('Messages Sent');
  cy.contains('View Overlay').click();
  cy.contains('What your assistant noticed');
  cy.contains('View Replay').click();
  cy.contains('Demo Replay Debugger');
  cy.visit('/assistants/prompt_pal/trust_profile/');
  cy.contains('Trust & Signals');
  cy.visit('/assistants/prompt_pal/trail');
  cy.contains('Journey Recap');
  cy.visit('/assistants/prompt_pal/growth/');
  cy.contains('Growth Track');
});
