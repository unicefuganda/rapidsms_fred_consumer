Feature: Fred Configuration page

  Scenario: FRED API settings
    Given I am logged in
    Given I have no configurations stored
    And I am on the Fred landing page
    Then I should see all the fields
    And I enter new configurations
    Then I should see all the fields populated with values
    And I should see success message
    And I change the configurations
    Then I should see all the fields populated with values
    And I should see success message

  Scenario: Job Status
    Given I have no previous job
    And I am on the Fred landing page
    And I start a job
    Then I should see pending current job with timestamp
    And I terminate the job
    And I should see option to start a job

  Scenario: Processing Facility - Reversion
    Given I process a facility
    And I should see reversion logs