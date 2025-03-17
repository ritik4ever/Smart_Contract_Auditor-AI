document.addEventListener('DOMContentLoaded', function () {
    // Initialize CodeMirror
    const editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        mode: 'text/x-solidity',
        theme: 'dracula',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        autoCloseBrackets: true,
        matchBrackets: true,
        gutters: ["CodeMirror-linenumbers"],
        viewportMargin: Infinity
    });

    // Button event listeners
    document.getElementById('scanBtn').addEventListener('click', scanContract);
    document.getElementById('loadSampleBtn').addEventListener('click', loadSampleContract);
    document.getElementById('clearBtn').addEventListener('click', () => {
        editor.setValue('');
        hideResults();
    });

    // API endpoint
    const API_URL = 'http://localhost:5000/api/scan';

    // Function to scan contract
    async function scanContract() {
        const contractCode = editor.getValue().trim();

        if (!contractCode) {
            showError('Please enter a smart contract to scan.');
            return;
        }

        showLoading(true);
        hideResults();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ contract_code: contractCode })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Error scanning contract:', error);
            showError('An error occurred while scanning the contract. Please try again later.');
        } finally {
            showLoading(false);
        }
    }

    // Function to display results
    function displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.classList.remove('d-none');

        // Display overview
        document.getElementById('overviewText').textContent = data.overview;

        // Display severity counts
        document.getElementById('highSeverityCount').textContent = data.stats.high_severity;
        document.getElementById('mediumSeverityCount').textContent = data.stats.medium_severity;
        document.getElementById('lowSeverityCount').textContent = data.stats.low_severity;

        // Display vulnerabilities
        const vulnerabilitiesList = document.getElementById('vulnerabilitiesList');
        vulnerabilitiesList.innerHTML = '';

        if (data.vulnerabilities.length === 0) {
            vulnerabilitiesList.innerHTML = '<div class="alert alert-success">No vulnerabilities detected!</div>';
            return;
        }

        data.vulnerabilities.forEach((vuln, index) => {
            const vulnerabilityCard = createVulnerabilityCard(vuln, index);
            vulnerabilitiesList.appendChild(vulnerabilityCard);
        });

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Function to create vulnerability card
    function createVulnerabilityCard(vuln, index) {
        const card = document.createElement('div');
        card.className = 'accordion-item vulnerability-card';

        // Determine severity class
        let severityClass = '';
        let severityBadgeClass = '';

        switch (vuln.severity) {
            case 'high':
                severityClass = 'vulnerability-high';
                severityBadgeClass = 'bg-danger';
                break;
            case 'medium':
                severityClass = 'vulnerability-medium';
                severityBadgeClass = 'bg-warning text-dark';
                break;
            case 'low':
                severityClass = 'vulnerability-low';
                severityBadgeClass = 'bg-info text-dark';
                break;
            default:
                severityBadgeClass = 'bg-secondary';
        }

        card.classList.add(severityClass);

        // Create heading
        const headingId = `heading${index}`;
        const collapseId = `collapse${index}`;

        // Create line numbers display
        let lineNumbersHtml = '';
        if (vuln.line_numbers && vuln.line_numbers.length > 0) {
            lineNumbersHtml = `<span class="line-numbers">Line${vuln.line_numbers.length > 1 ? 's' : ''}: ${vuln.line_numbers.join(', ')}</span>`;
        }

        card.innerHTML = `
            <h2 class="accordion-header" id="${headingId}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                    <span class="me-2">${capitalizeFirstLetter(vuln.type)}</span>
                    <span class="badge ${severityBadgeClass} vulnerability-badge">${vuln.severity.toUpperCase()}</span>
                    ${lineNumbersHtml}
                </button>
            </h2>
            <div id="${collapseId}" class="accordion-collapse collapse" aria-labelledby="${headingId}" data-bs-parent="#vulnerabilitiesList">
                <div class="accordion-body">
                    <p>${vuln.description}</p>
                    <div class="recommendations">
                        <h6>Recommendation:</h6>
                        <p>${vuln.recommendation}</p>
                    </div>
                </div>
            </div>
        `;

        return card;
    }

    // Function to load sample contract
    function loadSampleContract() {
        const sampleContract = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount);
        
        (bool sent, ) = msg.sender.call{value: _amount}("");
        require(sent, "Failed to send Ether");
        
        balances[msg.sender] -= _amount;
    }
    
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
    
    function getBlockTimestamp() public view returns (uint) {
        return block.timestamp;
    }
    
    function unsafeOperation(uint a, uint b) public pure returns (uint) {
        return a + b; // No overflow check
    }
}`;

        editor.setValue(sampleContract);
        hideResults();
    }

    // Helper functions
    function showLoading(isLoading) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        const scanBtn = document.getElementById('scanBtn');

        if (isLoading) {
            loadingSpinner.classList.remove('d-none');
            scanBtn.disabled = true;
        } else {
            loadingSpinner.classList.add('d-none');
            scanBtn.disabled = false;
        }
    }

    function hideResults() {
        document.getElementById('resultsSection').classList.add('d-none');
    }

    function showError(message) {
        document.getElementById('errorMessage').textContent = message;
        const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
        errorModal.show();
    }

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});