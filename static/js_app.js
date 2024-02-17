    var socket = io();

    socket.on('connect', function () {
        console.log('Websocket connected!');
        updateStatus();
		updateMarketGpuStatus();
		updateXuniFarmingStatus();
		emitPerfBotTableOutput();
		updateMiningStats();
		getInstanceUpdate();
    });

    socket.on('script_output', function (data) {
        addContent(data.data);
    });

    socket.on('perf_bot_output', function (data) {
        var node = document.createElement("DIV");
        var textnode = document.createTextNode(data.data);
        node.appendChild(textnode);
        document.getElementById("perf-bot-output").appendChild(node);
		updateScroll();
    });

function updateMiningStats() {
    fetch('/get-mining-stats')
        .then(response => response.text())
        .then(data => {
            document.getElementById('mining-stats').innerHTML = data;
        })
        .catch(error => console.error('Error fetching mining stats:', error));
}
setInterval(updateMiningStats, 300000);

	
function emitPerfBotTableOutput() {
    fetch('/emit-perf-bot-table-output')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Emitted table_output.html content successfully');
            } else {
                console.error('Error emitting table_output.html content:', data.message);
            }
        })
        .catch(error => {
            console.error('Error emitting table_output.html content:', error);
        });
}

socket.on('perf_bot_html', function (data) {
    try {
        document.getElementById('perf-bot-table').innerHTML = data.html;
    } catch (error) {
        console.error('Error updating content:', error);
    }
});


	
	socket.on('market_gpu_output', function (data) {
		addContentToMarket(data.data); 
	});
	
	socket.on('xuni_farming_output', function (data) {
		addContentToXuniFarming(data.data); 
	});

	socket.on('instance_rebuilder_output', function (data) {
		addContentToInstanceRebuilder(data.data);
	});
	
	socket.on('dust_removal_output', function (data) {
		addContentToDustRemover(data.data);
	});
	
    function startScript() {
        fetch('/start-script', {method: 'POST'})
            .then(response => response.text())
            .then(data => {
                alert(data);
                updateStatus();
            });
    }

    function stopScript() {
        fetch('/stop-script', {method: 'POST'})
            .then(response => response.text())
            .then(data => {
                alert(data);
                updateStatus();
            });
    }

	function updateStatus() {
		fetch('/script-status')
			.then(response => response.json())
			.then(data => {
				const statusElement = document.getElementById("status");
				statusElement.innerText = 'GPU Limit order: ' + data.status;
	
				// Show or hide the status box based on the status value
				if (data.status === 'Unknown' || data.status === 'running') {
					statusElement.style.display = 'block';
				} else if (data.status === 'stopped') {
					statusElement.style.display = 'none';
				}
			});
	}
	
	function updateMarketGpuStatus() {
		fetch('/market-gpu-status')
			.then(response => response.json())
			.then(data => {
				const statusElement = document.getElementById("marketGpuStatus");
				statusElement.innerText = 'GPU Market order: ' + data.status;
	
				// Show or hide the status box based on the status value
				if (data.status === 'Unknown' || data.status === 'running') {
					statusElement.style.display = 'block';
				} else if (data.status === 'stopped') {
					statusElement.style.display = 'none';
				}
			});
	}	
	
	function startMarketGpuScript() {
		fetch('/start-market-gpu-script', {method: 'POST'})
			.then(response => response.text())
			.then(data => {
				alert(data);
				updateMarketGpuStatus();
			});
	}
	
	function stopMarketGpuScript() {
		fetch('/stop-market-gpu-script', {method: 'POST'})
			.then(response => response.text())
			.then(data => {
				alert(data);
				updateMarketGpuStatus();
			});
	}
	
		function updateXuniFarmingStatus() {
		fetch('/xuni-farming-status')
			.then(response => response.json())
			.then(data => {
				const statusElement = document.getElementById("XuniFarmingStatus");
				statusElement.innerText = 'XUNI farming: ' + data.status;
	
				// Show or hide the status box based on the status value
				if (data.status === 'Unknown' || data.status === 'running') {
					statusElement.style.display = 'block';
				} else if (data.status === 'stopped') {
					statusElement.style.display = 'none';
				}
			});
	}	
	
	function startXuniFarmingScript() {
		fetch('/start-xuni-farming', {method: 'POST'})
			.then(response => response.text())
			.then(data => {
				alert(data);
				updateXuniFarmingStatus();
			});
	}
	
	function stopXuniFarmingScript() {
		fetch('/stop-xuni-farming', {method: 'POST'})
			.then(response => response.text())
			.then(data => {
				alert(data);
				updateXuniFarmingStatus();
			});
	}
	
	function startInstanceRebuilder() {
    fetch('/start-instance-rebuilder', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            alert(data);
  
        });
	}

	function startDustRemover() {
    fetch('/start-dust-removal', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            alert(data);
        });
	}
	
	
	// Call updateStatus every 5 seconds
	setInterval(updateStatus, 5000);

	function startPerfBot(showAlert = true) {
		// Clear previous output
		document.getElementById("perf-bot-output").innerHTML = '';
	
		// Add a query parameter to the request URL based on showAlert value
		const url = showAlert ? '/start-perf-bot' : '/start-perf-bot?silent=true';
	
		fetch(url, { method: 'POST' })
			.then(response => response.text())
			.then(data => {
				if (showAlert) {
					alert(data);
				}
				updateStatus();
			});
	}
	setInterval(() => startPerfBot(false), 200000);



    // Open the settings modal
    function openSettingsModal() {
        $('#settingsModal').modal('show');
    }

    // Close the settings modal
    function closeSettingsModal() {
        $('#settingsModal').modal('hide');
    }
	
		// Open the balance modal
	function openBalanceModal() {
		$('#balanceModal').modal('show');
	}
	
	// Close the balance modal
	function closeBalanceModal() {
		$('#balanceModal').modal('hide');
	}


	document.getElementById('gpu-deals-form').addEventListener('submit', function (e) {
		e.preventDefault();
		var formData = new FormData(this);
	
		fetch('/update-gpu-deals', {
			method: 'POST',
			body: formData,
		})
		.catch(error => {
			console.error('Error:', error);
			alert('Error updating GPU criteria');
		})
		.finally(() => {
			// Enable script buttons after GPU criteria update
			toggleScriptButtons(false);
		});
	});


    document.getElementById('settings-form').addEventListener('submit', function (event) {
        event.preventDefault();

        var apiKey = document.getElementById('api-key').value;
        var ethAddress = document.getElementById('eth-address').value;
        var sshKeyPath = document.getElementById('ssh-key-path').value; // Add this line
        var passphrase = document.getElementById('passphrase').value; // Add this line

        fetch('/update-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'api_key': apiKey,
                'eth_address': ethAddress,
                'ssh_key_path': sshKeyPath, // Include SSH Key Path
                'passphrase': passphrase // Include Passphrase
            })
        })
            .then(response => response.json())
            .then(data => {
                alert(data.status);
                closeSettingsModal();
				setTimeout(function() {
					window.location.reload();
				}, 1000);	
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating settings');
            });
    });
	
	
	
document.getElementById('market-gpu-config').addEventListener('submit', function (event) {
    event.preventDefault();

    var maxGpu = document.getElementById('max-gpu').value;
    var gpuMarket = document.getElementById('gpu-market').value;

    fetch('/market-gpu-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'max_gpu': maxGpu,
            'gpu_market': gpuMarket,
        })
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating settings');
    });
});



document.getElementById('xuni-farming-config').addEventListener('submit', function (event) {
    event.preventDefault();

    var xuniMaxGpu = document.getElementById('xuni-max-gpu').value;
    var xuniGpuMarket = document.getElementById('xuni-gpu-market').value;

    fetch('/xuni-farming-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'xuni_max_gpu': xuniMaxGpu,
            'xuni_gpu_market': xuniGpuMarket,
        })
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating settings');
    });
});

function submitForm(button) {
    event.preventDefault();
    var form = button.closest('form');

    var instanceID = form.querySelector('input[name="instance_id_destroy"]').value;

    fetch('/destroy_instance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'instance_id_destroy': instanceID,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error destroying instance');
    });
}

function submitRebootForm(button) {
    event.preventDefault();
    var form = button.closest('form');

    var instanceID = form.querySelector('input[name="instance_id_reboot"]').value;

    fetch('/reboot_instance', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'instance_id_reboot': instanceID,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); 
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error rebooting instance');
    });
}

function submitRebuildForm(button) {
    event.preventDefault();
    var form = button.closest('form');

    var instanceID = form.querySelector('input[name="instance_id_rebuild"]').value;

    fetch('/rebuild_link', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'instance_id_rebuild': instanceID,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); 
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error rebooting instance');
    });
}


document.getElementById('perf-bot-config').addEventListener('submit', function (event) {
    event.preventDefault();

    var sortColumnIndex = document.getElementById('sort-column-index').value;
    var sortOrder = document.getElementById('sort-order').value;
	var thresholdPerf = document.getElementById('threshold-perf').value;

    fetch('/perf-bot-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'sort_column_index': sortColumnIndex,
            'sort_order': sortOrder,
			'threshold': thresholdPerf,
        })
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating settings');
    });
});

document.getElementById('dust-removal-config').addEventListener('submit', function (event) {
    event.preventDefault();

    var removeScheduling = document.getElementById('remove-scheduling').checked;
    var removeInactive = document.getElementById('remove-inactive').checked;
    var removeOffline = document.getElementById('remove-offline').checked;
	
    fetch('/dust-removal-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'remove_scheduling': removeScheduling ? 'on' : 'off',
            'remove_inactive': removeInactive ? 'on' : 'off',
            'remove_offline': removeOffline ? 'on' : 'off',
        })
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating settings');
    });
});



var currentMarketDPH = {}; // Cache for storing fetched data
var lastFetchTime = 0; // Timestamp of the last data fetch

function isDataFresh() {
    const maxAge = 5 * 60 * 1000; // Maximum age of the data in milliseconds (5 minutes)
    return Date.now() - lastFetchTime < maxAge;
}

function processData(data) {
    const lines = data.split('\n');
    lines.forEach(line => {
        const [gpuName, value] = line.split(':').map(part => part.trim());
        if (gpuName && value) {
            currentMarketDPH[gpuName] = value;
        }
    });
    lastFetchTime = Date.now(); // Update the timestamp
    updateMarketPrices(); // Update market prices in all rows
}

async function getCurrentDPH(forceUpdate = false) {
    if (!isDataFresh() || forceUpdate) {
        try {
            const response = await fetch('/get-current-dph');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.status === 'success') {
                processData(data.output); // Process and store the data
            } else {
                console.error('Error fetching data:', data.output);
            }
        } catch (error) {
            console.error('Error:', error.message);
        }
    } else {
        console.log('Using cached data');
        updateMarketPrices(); // Update the UI using the cached data
    }
}

getCurrentDPH(true); // Force initial data fetch

setInterval(() => getCurrentDPH(true), 120000); 


function updateMarketPrices() {
    document.querySelectorAll('.gpu-dropdown').forEach(dropdown => {
        const selectedGPU = dropdown.value;
        const marketPriceInput = dropdown.closest('tr').querySelector('.market-price');
        if (currentMarketDPH[selectedGPU] && marketPriceInput) {
            marketPriceInput.value = currentMarketDPH[selectedGPU]; // Ensure this is the correct way to set the value for your input
        }
    });
}



var selectedGPUs = [];

// Initialize selectedGPUs with GPU names already selected in existing rows
document.querySelectorAll(".gpu-dropdown").forEach(function (dropdown) {
    var selectedGPU = dropdown.value;
    if (selectedGPU && !selectedGPUs.includes(selectedGPU)) {
        selectedGPUs.push(selectedGPU);
    }
});

// Now, update the dropdowns for existing rows
document.querySelectorAll(".gpu-dropdown").forEach(updateDropdownOptions);

function updateDropdownOptions(gpuDropdown) {
    var gpuOptions = ["RTX 4090", "RTX 3090", "RTX 3060", "RTX A6000", "RTX A5000", "RTX A4000", "A40"];
    var currentSelection = gpuDropdown.value;
    gpuDropdown.innerHTML = ''; // Clear existing options first

    var firstOptionAdded = false; // Flag to track if the first option has been added

    gpuOptions.forEach(function(gpu) {
        if (!selectedGPUs.includes(gpu) || gpu === currentSelection) {
            var option = document.createElement("option");
            option.value = gpu;
            option.text = gpu;
            
            if (!firstOptionAdded || gpu === currentSelection) {
                option.selected = true; // Mark the first available option or current selection as selected
                firstOptionAdded = true; // Update the flag once the first option is added
            }

            gpuDropdown.appendChild(option);
        }
    });

    // Update the current selection if it's not in the options and the dropdown has options
    if (!gpuOptions.includes(currentSelection) && gpuDropdown.options.length > 0) {
        gpuDropdown.options[0].selected = true; // Select the first option by default
        selectedGPUs.push(gpuDropdown.options[0].value); // Add the first option to selectedGPUs if not included
    }
}


// Add the event listener for the existing dropdowns to handle changes
document.querySelectorAll(".gpu-dropdown").forEach(function (dropdown) {
    dropdown.addEventListener("change", function (e) {
        // Handle the change event as described in your original code
        // This includes updating selectedGPUs and possibly updating other dropdowns
    });
});

// Function to add a new row
function addRow() {
    var table = document.getElementById("gpu-table").getElementsByTagName('tbody')[0];
    if (table.rows.length < 7) {
        var newRow = table.insertRow();

        var cell0 = newRow.insertCell(0);
        cell0.innerHTML = '<button type="button" class="btn btn-danger btn-sm" onclick="removeRow(this)">X</button>';

        var cell1 = newRow.insertCell(1);
        var cell2 = newRow.insertCell(2);
        var cell3 = newRow.insertCell(3);

        var gpuDropdown = document.createElement("select");
        gpuDropdown.className = "form-control gpu-dropdown";
        gpuDropdown.name = "gpu_name[]";
        updateDropdownOptions(gpuDropdown); // Populate dropdown options

        var limitPriceInput = document.createElement("input");
        limitPriceInput.type = "number";
        limitPriceInput.step = "0.001";
        limitPriceInput.className = "form-control";
        limitPriceInput.name = "dph_rate[]";
        limitPriceInput.placeholder = "Your Limit price";
        limitPriceInput.required = true;
        
        // Bind the validation function to the new limit price input
        limitPriceInput.addEventListener('change', validateLimitPrice);

        cell1.appendChild(gpuDropdown);
        cell2.appendChild(limitPriceInput);
        cell3.innerHTML = '<input type="text" class="form-control market-price" value="" disabled>';

        updateMarketPrices(); // Update market prices for the new row
    } else {
        alert("You can add a maximum of 7 rows.");
    }
}



// Function to remove a row
function removeRow(button) {
    var row = button.closest("tr");
    if (row) {
        var gpuDropdown = row.querySelector(".gpu-dropdown");
        if (gpuDropdown) {
            // Remove the selected GPU from the tracking array
            var selectedValue = gpuDropdown.value;
            var index = selectedGPUs.indexOf(selectedValue);
            if (index !== -1) {
                selectedGPUs.splice(index, 1);
            }
        }
        row.remove();

        // Update dropdowns in remaining rows to reflect the current selections
        document.querySelectorAll(".gpu-dropdown").forEach(function (dropdown) {
            updateDropdownOptions(dropdown);
        });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Add event listeners to all limit price inputs
    document.querySelectorAll('input[name="dph_rate[]"]').forEach(input => {
        input.addEventListener('change', validateLimitPrice);
    });
});

function validateLimitPrice(event) {
    const limitPriceInput = event.target;
    const limitPrice = parseFloat(limitPriceInput.value); // Convert input value to float for comparison

    const gpuDropdown = limitPriceInput.closest('tr').querySelector('.gpu-dropdown');
    const selectedGPU = gpuDropdown.value;

    const marketPriceInput = limitPriceInput.closest('tr').querySelector('.market-price');
    const marketPrice = parseFloat(marketPriceInput.value); // Convert market price value to float for comparison

    // Check if the limit price is greater than or equal to the market price
    if (limitPrice >= marketPrice) {
        alert("Limit price must be less than the current market price.");
        limitPriceInput.value = ''; // Optionally clear the invalid input
        // Implement any other UI indication for invalid input as needed
    }
}




	function updateScroll() {
		var elementOutput = document.getElementById("output");
		elementOutput.scrollTop = elementOutput.scrollHeight;
	
		var elementMarket = document.getElementById("output_market");
		elementMarket.scrollTop = elementMarket.scrollHeight;

		var elementMarket = document.getElementById("xuni_farming_output");
		elementMarket.scrollTop = elementMarket.scrollHeight;
		
		var elementOutput = document.getElementById("instance-rebuilder-output");
		elementOutput.scrollTop = elementOutput.scrollHeight;
		
		var elementOutput = document.getElementById("perf-bot-output");
		elementOutput.scrollTop = elementOutput.scrollHeight;	

		var elementOutput = document.getElementById("dust_removal_output");
		elementOutput.scrollTop = elementOutput.scrollHeight;		
	}
	

    function addContent(newContent) {
        var outputDiv = document.getElementById("output");
        var node = document.createElement("DIV");
        var textnode = document.createTextNode(newContent);
        node.appendChild(textnode);
        outputDiv.appendChild(node);
        updateScroll();
    }
	function addContentToMarket(newContent) {
		var outputDiv = document.getElementById("output_market");
		var node = document.createElement("DIV");
		var textnode = document.createTextNode(newContent);
		node.appendChild(textnode);
		outputDiv.appendChild(node);
		updateScroll();
	}
		function addContentToXuniFarming(newContent) {
		var outputDiv = document.getElementById("xuni_farming_output");
		var node = document.createElement("DIV");
		var textnode = document.createTextNode(newContent);
		node.appendChild(textnode);
		outputDiv.appendChild(node);
		updateScroll();
	}
	function addContentToInstanceRebuilder(newContent) {
		var outputDiv = document.getElementById("instance-rebuilder-output");
		var node = document.createElement("DIV");
		var textnode = document.createTextNode(newContent);
		node.appendChild(textnode);
		outputDiv.appendChild(node);
		updateScroll();
	}	
	
	function addContentToDustRemover(newContent) {
		var outputDiv = document.getElementById("dust_removal_output");
		var node = document.createElement("DIV");
		var textnode = document.createTextNode(newContent);
		node.appendChild(textnode);
		outputDiv.appendChild(node);
		updateScroll();
	}	


// Global variable to track if openConfigWizard() is initiated
var openConfigWizardInitiated = false;

// Function to open the configuration wizard modal
function openConfigWizard() {
    openConfigWizardInitiated = true;

    // Hide all steps except for Step 1
    $('.config-step').hide();
    $('#step1').show();

    // Show the iframe for Step 1, Step 2, and Step 3
    $('#step123Iframe').show();

    $('#configWizardModal').modal('show');
	
	// Call appendIframeIfNeeded() after updating the flag
    appendIframeIfNeeded();
}

// Function to close the configuration wizard modal
function closeConfigWizard() {
    $('#configWizardModal').modal('hide');
}

// Function to check if the iframe needs to be appended
function appendIframeIfNeeded() {
    var configWizardCompletedStr = document.body.getAttribute('data-config-wizard');
    var configWizardCompleted = configWizardCompletedStr === 'true';

    if (openConfigWizardInitiated || !configWizardCompleted) {
        var iframeExists = $('#iframe_vast').find('#step123Iframe').length > 0;
        if (!iframeExists) {
            $('#iframe_vast').html('<iframe id="step123Iframe" src="https://cloud.vast.ai/?ref_id=89943" style="width:100%; height:500px;"></iframe>');
        }
    }
}


// Check if iframe needs to be appended when the page is loaded
document.addEventListener('DOMContentLoaded', function() {
    appendIframeIfNeeded();
});

function nextStep(stepNumber) {
    // Hide the current step
    document.getElementById('step' + stepNumber).style.display = 'none';

    // Show the next step
    document.getElementById('step' + (stepNumber + 1)).style.display = 'block';
}

function prevStep(stepNumber) {
    // Hide the current step
    document.getElementById('step' + stepNumber).style.display = 'none';

    // Show the previous step
    document.getElementById('step' + (stepNumber - 1)).style.display = 'block';
}


// Function to submit the configuration data
document.getElementById('wizzard-form').addEventListener('submit', function (event) {
    event.preventDefault();  // Prevents the default form submission action

    var apiKey = document.getElementById('api-key-wizz').value;
    var ethAddress = document.getElementById('eth-address-wizz').value;
    var sshKeyPath = document.getElementById('ssh-key-path-wizz').value;

    fetch('/update-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'api_key': apiKey,
            'eth_address': ethAddress,
            'ssh_key_path': sshKeyPath,
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.status);
        closeConfigWizard();  // Close the Configuration Wizard
        // Refresh the page after a short delay to ensure modal has time to close
        setTimeout(function() {
            window.location.reload(); // Reload the page
        }, 1000); // Delay in milliseconds
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating settings');
    });
});

document.getElementById('generate-ssh-key-btn').addEventListener('click', function () {
    fetch('/generate-ssh-key')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const outputDiv = document.getElementById('ssh-key-output');
                outputDiv.innerHTML = ''; // Clear previous output

                // Find the index of "Public Key:" and "Private key path:"
                const publicKeyIndex = data.output.indexOf('Public Key:');
                const privateKeyPathIndex = data.output.indexOf('Private key path:');

                // Append "SSH key found." and add a new line before "Public Key:"
                if (publicKeyIndex !== -1) {
                    const sshKeyFoundText = data.output.substring(0, publicKeyIndex).trim();
                    outputDiv.appendChild(document.createTextNode(sshKeyFoundText));
                    outputDiv.appendChild(document.createElement('br')); // New line before "Public Key:"
                }

                // Extract, append the "Public Key:" part, and add the key inside the box
                if (privateKeyPathIndex !== -1) {
                    const publicKeyIntroText = data.output.substring(publicKeyIndex, publicKeyIndex + 'Public Key:'.length).trim();
                    outputDiv.appendChild(document.createTextNode(publicKeyIntroText));

                    const publicKey = data.output.substring(publicKeyIndex + 'Public Key:'.length, privateKeyPathIndex).trim();
                    const publicKeyBox = document.createElement('span');
                    publicKeyBox.className = 'key-box';
                    publicKeyBox.textContent = publicKey;
                    outputDiv.appendChild(publicKeyBox);

                    // Create and append the "Copy" button with type set to 'button'
                    const copyBtn = document.createElement('button');
                    copyBtn.textContent = 'Copy';
                    copyBtn.className = 'btn btn-secondary btn-sm ml-2'; // Bootstrap classes for styling
                    copyBtn.type = 'button'; // Important to prevent form submission
                    outputDiv.appendChild(copyBtn);

                    // Event listener for the "Copy" button
                    copyBtn.addEventListener('click', function (event) {
                        event.preventDefault(); // Prevent any form submission
                        navigator.clipboard.writeText(publicKey).then(() => {
                            alert('Public Key copied to clipboard!');
                        }, (err) => {
                            console.error('Error copying text to clipboard', err);
                        });
                    });
                }

                // Extract the "Private key path:" part and autofill the hidden input field
                // The path and label are not appended to the outputDiv, making them invisible to the user
                if (privateKeyPathIndex !== -1) {
                    const privateKeyPathText = data.output.substring(privateKeyPathIndex).trim();
                    const parts = privateKeyPathText.split(':');
                    if (parts.length > 1) {
                        const privateKeyPath = parts.slice(1).join(':').trim(); // Join back if there were multiple colons
                        
                        // Autofill the input field for the private key path
                        document.getElementById('ssh-key-path-wizz').value = privateKeyPath;
                    }
                }
            } else {
                alert('Error generating SSH key: ' + data.output);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error generating SSH key');
        });
});

// Open config wizzard on start if "CONFIG_WIZARD": false
document.addEventListener('DOMContentLoaded', function() {
    // Handle the configuration wizard if not completed
    var configWizardCompletedStr = document.body.getAttribute('data-config-wizard');
    var configWizardCompleted = configWizardCompletedStr === 'true';
    if (!configWizardCompleted) {
        openConfigWizard();  // Assuming openConfigWizard() is defined elsewhere
    }

    // Handle the donation form submission
    document.getElementById('donation-form').addEventListener('submit', function(e) {
        e.preventDefault();  // Prevent the default form submission

        // Extract the donation amount from the form
        var donationAmount = document.getElementById('donationAmount').value;

        // Prepare the data to be sent in the request
        var formData = new FormData();
        formData.append('donation_amount', donationAmount);

        // Send the AJAX request to the /donate route
        fetch('/donate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
           
            alert(data.message);  
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });

    // Theme toggle functionality
    var isDarkTheme = document.body.getAttribute('data-dark-theme') === 'True';
    var stylesheet = document.getElementById('stylesheet');
    var theme = isDarkTheme ? 'dark-style.css' : 'styles.css';
    stylesheet.setAttribute('href', '/static/' + theme);  // Adjusted to a direct path

    document.getElementById('theme-toggle').addEventListener('click', function(event) {
        event.preventDefault();  // Prevent the default anchor action

        // Toggle the theme
        isDarkTheme = !isDarkTheme;  // Flip the isDarkTheme boolean
        theme = isDarkTheme ? 'dark-style.css' : 'styles.css';
        stylesheet.setAttribute('href', '/static/' + theme);  // Adjusted to a direct path

        // AJAX request to update server-side config
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/toggle-theme', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({darkTheme: isDarkTheme}));

        xhr.onload = function() {
            if (xhr.status === 200) {
                console.log('Theme updated successfully');
            } else {
                console.error('Error updating theme');
            }
        };
    });
});


// Function to enable/disable script buttons
function toggleScriptButtons(disabled) {
    document.getElementById("start-script-button").disabled = disabled;
    document.getElementById("stop-script-button").disabled = disabled;
	document.getElementById("start-market-gpu-script").disabled = disabled;
    document.getElementById("stop-market-gpu-script").disabled = disabled;
	document.getElementById("start-xuni-farming").disabled = disabled;
    document.getElementById("stop-xuni-farming").disabled = disabled;	
}

function setHoverTextForDisabledButtons(startScriptButton, stopScriptButton, startMarketGpuButton, stopMarketGpuButton, startXuniFarmingButton, stopXuniFarmingButton, balance) {
    if (balance <= 0) {
        startScriptButton.title = "Your Vast.ai balance is $0.00. Add funds to your account to start.";
        stopScriptButton.title = "Your Vast.ai balance is $0.00. Add funds to your account to start.";
        startMarketGpuButton.title = "Your Vast.ai balance is $0.00. Add funds to your account to start.";
        stopMarketGpuButton.title = "Your Vast.ai balance is $0.00. Add funds to your account to start.";
        startXuniFarmingButton.title = "Your Vast.ai balance is $0.00. Add funds to your account to start.";
        stopXuniFarmingButton.title = "Your Vast.ai balance is $0.00. Add funds to your account to start.";		
    } else {
        startScriptButton.removeAttribute("title");
        stopScriptButton.removeAttribute("title");
        startMarketGpuButton.removeAttribute("title");
        stopMarketGpuButton.removeAttribute("title");
		startXuniFarmingButton.removeAttribute("title");
        stopXuniFarmingButton.removeAttribute("title");
    }
}


function fetchBalanceInfo() {
    fetch('/get-balance-info')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Split the output by line breaks to handle multiple lines of information
                const outputLines = data.output.trim().split('\n');

                // Update the credit info with the fetched value (first line)
                const creditInfoElement = document.getElementById('balance-info-output');
                creditInfoElement.textContent = outputLines[0]; // Only the first line for credit info

                // Update the additional balance info with all lines (including the first line)
                const additionalInfoElement = document.getElementById('additional-balance-info');
                const additionalInfo = outputLines.join('<br>'); // Use <br> to maintain line breaks in HTML
                additionalInfoElement.innerHTML = additionalInfo;

                // Logic to enable/disable buttons based on the balance
                // Extract the balance value from the first line
                if (outputLines[0].startsWith('Vast.ai credit: $')) {
                    const balance = parseFloat(outputLines[0].slice('Vast.ai credit: $'.length));
                    const startScriptButton = document.getElementById('start-script-button');
                    const stopScriptButton = document.getElementById('stop-script-button');
                    const startMarketGpuScript = document.getElementById('start-market-gpu-script');
                    const stopMarketGpuScript = document.getElementById('stop-market-gpu-script');
					const startXuniFarmingButton = document.getElementById('start-xuni-farming');
                    const stopXuniFarmingButton = document.getElementById('stop-xuni-farming');

                    if (balance <= 0) {
                        toggleScriptButtons(true); // Disable both buttons
                    } else {
                        toggleScriptButtons(false); // Enable both buttons
                    }

                    // Continue with the existing logic for setting hover text for disabled buttons
                    setHoverTextForDisabledButtons(startScriptButton, stopScriptButton, startMarketGpuScript, stopMarketGpuScript, startXuniFarmingButton, stopXuniFarmingButton, balance);
                } else {
                    console.error('Invalid balance format:', outputLines[0]);
                }
            } else {
                console.error('Error fetching balance info:', data.output);
            }
        })
        .catch(error => console.error('Error:', error));
}


function getInstanceUpdate() {
    fetch('/get-instance-update')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}
setInterval(getInstanceUpdate(), 6000);

function updateInstances() {
    fetch('/get-instances-data')
        .then(response => response.json())
        .then(data => {
            const instances = data.instances;
            let htmlContent = '';
            if (instances && instances.length > 0) {
                instances.forEach(instance => {
                    htmlContent += `
                        <table class="table mb-3" style="margin: 10px auto;">
                            <tbody class="instances-container">
                                <tr>
                                    <td style="width: 20%;"><input type="checkbox" name="instance_ids" style="margin-right:10px;" value="${instance['instance_id']}"><strong>Instance ID:</strong> ${instance['instance_id']}</td>
                                    <td><span style="font-size: 90%;" class="badge ${instance['verification'] === 'verified' ? 'badge-success' : 'badge-warning'}">${instance['verification']}</span>&nbsp&nbsp&nbsp<strong>Machine ID:</strong> ${instance['machine_id']}&nbsp&nbsp&nbsp<strong>Host ID:</strong> ${instance['host_id']}&nbsp&nbsp&nbsp<strong>Location:</strong> ${instance['geolocation']}</td>
                                    <td style="width: 23%;text-align: right;">
                                        <form id="reboot-instance-form">
                                            <input type="hidden" id="instance_id_reboot" name="instance_id_reboot" value="${instance['instance_id_reboot']}">
                                            <button type="button" style="padding: 0.0rem .3rem;" class="btn btn-primary btn-sm" onclick="submitRebootForm(this)">REBOOT</button>
                                        </form>
                                        <form id="rebuild-instance-form">
                                            <input type="hidden" id="instance_id_rebuild" name="instance_id_rebuild" value="${instance['instance_id_rebuild']}">
                                            <button type="button" style="padding: 0.0rem .3rem;" class="btn btn-warning btn-sm" onclick="submitRebuildForm(this)">REBUILD</button>
                                        </form>
                                        <form id="destroyForm">
                                            <input type="hidden" id="instance_id_destroy" name="instance_id_destroy" value="${instance['instance_id_destroy']}">
                                            <button type="button" style="padding: 0.0rem .3rem;" class="btn btn-danger btn-sm" onclick="submitForm(this)">DESTROY</button>
                                        </form>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width: 20%;">
                                        <div style="display: flex; align-items: center;">
                                            <strong style="margin-right: 5px;">GPU:</strong>
                                            <span>${instance['gpu_util']}%</span>
                                            <div class="progress ml-2" style="height: 5px;width: 30%; flex-grow: 1;">
                                                <div class="progress-bar bg-primary" role="progressbar" style="width: ${instance['gpu_util']}%;"></div>
                                            </div>
                                        </div>                                    
                                        <div style="display: flex; align-items: center;">
                                            <strong style="margin-right: 5px;">CPU:</strong>
                                            <span>${instance['cpu_util']}%</span>
                                            <div class="progress ml-2" style="height: 5px; flex-grow: 1;">
                                                <div class="progress-bar bg-success" role="progressbar" style="width: ${instance['cpu_util']}%;"></div>
                                            </div>
                                        </div>
                                        <div style="display: flex; align-items: center;">
                                            <strong style="margin-right: 5px;">HDD:</strong>
                                            <span>${instance['hdd_usage']}%</span>
                                            <div class="progress ml-2" style="height: 5px; flex-grow: 1;">
                                                <div class="progress-bar bg-warning" role="progressbar" style="width: ${instance['hdd_usage']}%;"></div>
                                            </div>
                                        </div>
                                        <strong>VRAM:</strong> ${instance['gpu_ram_used_gb']}GB / ${instance['gpu_ram_gb']}GB 
                                    </td>
                                    <td>
                                        <p class="gpu_name_instances">
                                        ${instance['num_gpus']}x ${instance['gpu_name']} &nbsp;&nbsp;&nbsp;&nbsp;
                                        <span class="badge ${instance['actual_status'] === 'running' ? 'badge-success' : instance['actual_status'] === 'offline' ? 'badge-danger' : 'badge-warning'} gpu_status_badge">
                                            ${instance['actual_status']} 
                                        </span> &nbsp;&nbsp;&nbsp;&nbsp;<br>
                                        <p class="mining_stats">
                                            <b>Hash rate:</b> ${instance['hash_rate']} h/s &nbsp;&nbsp;
                                            <span style="color: #dc3545;"><b>super:</b></span> ${instance['super_blocks']} &nbsp;&nbsp;
                                            <span style="color: #28a745;"><b>normal:</b></span> ${instance['normal_blocks']} &nbsp;&nbsp;
                                            <span style="color: #ffc107;"><b>xuni:</b></span> ${instance['xuni_blocks']}
                                        </p>
                                    </td>
                                    <td style="width: 23%; text-align: center;">
                                        <strong>Age:</strong> ${instance['age']} <br>
                                        <strong>Remaining:</strong> ${instance['duration']}<br>
                                        <button type="button" style="padding: 0.0rem .3rem;" class="btn btn-secondary btn-sm" onclick="copyToClipboard('${instance['ssh_link']}')">COPY SSH COMMAND</button>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width: 20%;"><strong>Label:</strong> ${instance['label'] || 'No Label'}</td>
                                    <td><strong>Status Message:</strong> ${instance['status_msg']}</td>
                                    <td style="width: 23%; text-align: right; font-size:16px"><strong>$${instance['dph_total']}/hr&nbsp&nbsp</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    `;
                });
            } else {
                htmlContent = '<p>No instances available.</p>';
            }
            document.getElementById('instancesTab').innerHTML = htmlContent;
        })
        .catch(error => console.error('Error fetching instances:', error));
}

// Call updateInstances initially and every 6000 milliseconds (6 seconds)
updateInstances();
setInterval(updateInstances, 6000);



document.addEventListener('DOMContentLoaded', () => {
    // Code that runs when the DOM is fully loaded
    fetchBalanceInfo(); // Call the function once immediately
    setInterval(fetchBalanceInfo, 60000);

    // Add a click event listener to the "balance-info-output" element
    const creditInfoElement = document.getElementById('balance-info-output');
    creditInfoElement.addEventListener('click', () => {
        openBalanceModal();
    });
});


document.querySelectorAll('.tool-tile').forEach(tile => {
    tile.addEventListener('click', function(event) {
        // Check if the clicked element is a button or within the 'click-exception' table
        if (!event.target.matches('button') && !event.target.closest('#click-exception')) {
            // Toggle display of '.tool-content' only if the clicked element is not a button and not inside the 'click-exception' table
            this.querySelector('.tool-content').style.display = this.querySelector('.tool-content').style.display === 'none' ? 'block' : 'none';
        }
    });
});
document.querySelector('#start-dust-removal-button').addEventListener('click', function(event) {
    event.stopPropagation(); // Prevent click event from propagating to parent (.tool-tile)
    startDustRemover(); // Call your function to start the dust removal process
});
document.querySelector('#start-instance-rebuilder-button').addEventListener('click', function(event) {
    event.stopPropagation(); // Prevent click event from propagating to parent (.tool-tile)
    startInstanceRebuilder(); // Call your function to start the instance rebuilding process
});



document.querySelector('.eth-address').addEventListener('click', function() {
    this.select(); // Selects the text inside the input
    document.execCommand('copy'); // Copies the selected text to clipboard
    alert('Ethereum address copied to clipboard.'); // Alert or another form of notification
});

document.addEventListener('DOMContentLoaded', function() {
  var toggleButton = document.getElementById('toggleWidthButton');
  var perfBotTable = document.getElementById('perf-bot-table');

  toggleButton.addEventListener('click', function() {
    perfBotTable.classList.toggle('full-width');
  });
});

  function copyToClipboard(text) {
    var textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");  
    document.body.removeChild(textarea);
    alert("Copied to clipboard:\n\n" + text);
  }
