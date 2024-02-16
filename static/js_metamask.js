    document.addEventListener('DOMContentLoaded', function() {
        const btn = document.getElementById('add-xenium-network');

        btn.addEventListener('click', async function() {
            btn.disabled = true; // Disable the button
            btn.innerText = "Processing...";

            if (typeof window.ethereum !== 'undefined') {
                try {
                    const result = await window.ethereum.request({
                        method: "wallet_addEthereumChain",
                        params: [{
                            chainId: "0x18705",  // Hexadecimal representation of 100101
                            rpcUrls: ["https://xenblocks.io:5556/"],
                            chainName: "XenBlocks",
                            nativeCurrency: {
                                name: "XNM",
                                symbol: "XNM",
                                decimals: 18
                            },
                            blockExplorerUrls: null // Set to null as per MetaMask's requirements
                        }]
                    });
                    if (result === null) {
                        btn.innerText = "XenBlocks network added successfully!";
                    }
                } catch (error) {
                    btn.innerText = "Error adding XenBlocks network";
                    console.log("Error adding XenBlocks network: ", error.message);
                } finally {
                    setTimeout(() => {
                        btn.innerText = "Add XenBlocks Network to MetaMask";
                        btn.disabled = false; // Re-enable the button after a delay
                    }, 3000);
                }
            } else {
                btn.innerText = "MetaMask is not installed";
                setTimeout(() => {
                    btn.innerText = "Add XenBlocks Network to MetaMask";
                    btn.disabled = false; // Re-enable the button after a delay
                }, 3000);
            }
        });
    });
	
    document.addEventListener('DOMContentLoaded', function() {
        const xblkBtn = document.getElementById('add-xblk-token');

        xblkBtn.addEventListener('click', function() {
            xblkBtn.disabled = true;
            xblkBtn.innerText = "Adding X.BLK Token...";
            switchAndAddToken(
                "X.BLK",
                "0x999999cf1046e68e36e1aa2e0e07105eddd00001",
                18,
                xblkBtn
            );
        });

        async function switchToXeniumNetwork() {
            try {
                await window.ethereum.request({
                    method: "wallet_addEthereumChain",
                    params: [{
                        chainId: "0x18705",
                        rpcUrls: ["https://xenblocks.io:5556"],
                        chainName: "XenBlocks",
                        nativeCurrency: {
                            name: "XNM",
                            symbol: "XNM",
                            decimals: 18
                        },
                        blockExplorerUrls: null
                    }]
                });
            } catch (error) {
                console.error("Error switching to Xenium network:", error);
            }
        }

        async function switchAndAddToken(symbol, address, decimals, btn) {
            const currentChainId = await window.ethereum.request({ method: 'eth_chainId' });
            if (currentChainId !== "0x18705") {
                await switchToXeniumNetwork();
            }

            addToken(symbol, address, decimals, btn);
        }

        async function addToken(symbol, address, decimals, btn) {
            try {
                const wasAdded = await window.ethereum.request({
                    method: 'wallet_watchAsset',
                    params: {
                        type: 'ERC20',
                        options: {
                            address: address,
                            symbol: symbol,
                            decimals: decimals,
                            image: 'IMAGE_URL', // Optionally, add an image URL for the token logo
                        },
                    },
                });

                if (wasAdded) {
                    btn.innerText = `${symbol} added successfully!`;
                    setTimeout(() => {
                        btn.innerText = `Add ${symbol} Token to MetaMask`;
                        btn.disabled = false;
                    }, 3000);
                } else {
                    btn.innerText = `Error adding ${symbol}`;
                    setTimeout(() => {
                        btn.innerText = `Add ${symbol} Token to MetaMask`;
                        btn.disabled = false;
                    }, 3000);
                }
            } catch (error) {
                console.error(error);
                btn.innerText = `Error adding ${symbol}`;
                setTimeout(() => {
                    btn.innerText = `Add ${symbol} Token to MetaMask`;
                    btn.disabled = false;
                }, 3000);
            }
        }
    });

    document.addEventListener('DOMContentLoaded', function() {
        const xuniBtn = document.getElementById('add-xuni-token');

        xuniBtn.addEventListener('click', function() {
            xuniBtn.disabled = true;
            xuniBtn.innerText = "Adding XUNI Token...";
            switchAndAddToken(
                "XUNI",
                "0x999999cf1046e68e36e1aa2e0e07105eddd00002",
                18,
                xuniBtn
            );
        });

        async function switchToXeniumNetwork() {
            try {
                await window.ethereum.request({
                    method: "wallet_addEthereumChain",
                    params: [{
                        chainId: "0x18705",
                        rpcUrls: ["https://xenblocks.io:5556"],
                        chainName: "XenBlocks",
                        nativeCurrency: {
                            name: "XNM",
                            symbol: "XNM",
                            decimals: 18
                        },
                        blockExplorerUrls: null
                    }]
                });
            } catch (error) {
                console.error("Error switching to Xenium network:", error);
            }
        }

        async function switchAndAddToken(symbol, address, decimals, btn) {
            const currentChainId = await window.ethereum.request({ method: 'eth_chainId' });
            if (currentChainId !== "0x18705") {
                await switchToXeniumNetwork();
            }

            addToken(symbol, address, decimals, btn);
        }

        async function addToken(symbol, address, decimals, btn) {
            try {
                const wasAdded = await window.ethereum.request({
                    method: 'wallet_watchAsset',
                    params: {
                        type: 'ERC20',
                        options: {
                            address: address,
                            symbol: symbol,
                            decimals: decimals,
                            image: 'IMAGE_URL', // Optionally, add an image URL for the token logo
                        },
                    },
                });

                if (wasAdded) {
                    btn.innerText = `${symbol} added successfully!`;
                    setTimeout(() => {
                        btn.innerText = `Add ${symbol} Token to MetaMask`;
                        btn.disabled = false;
                    }, 3000);
                } else {
                    btn.innerText = `Error adding ${symbol}`;
                    setTimeout(() => {
                        btn.innerText = `Add ${symbol} Token to MetaMask`;
                        btn.disabled = false;
                    }, 3000);
                }
            } catch (error) {
                console.error(error);
                btn.innerText = `Error adding ${symbol}`;
                setTimeout(() => {
                    btn.innerText = `Add ${symbol} Token to MetaMask`;
                    btn.disabled = false;
                }, 3000);
            }
        }
    });	
	