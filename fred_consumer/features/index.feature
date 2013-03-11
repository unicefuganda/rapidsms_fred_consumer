Feature: Fred Configuration page

 Scenario: FRED consumer page
   Given I am logged in
   And I am on the Fred landing page
   Then I should see all the fields

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

  Scenario: Processing Facility - Create
    Given I process a new facility
    And I should see new reversion logs for the latest facility

  Scenario: Failures page
    Given I have few failures from Fred sync
    And I am on the Fred failures page
    Then I should see failures paginated