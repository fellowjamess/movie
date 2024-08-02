// ==UserScript==
// @name         Letterboxd Special Effect
// @namespace    none
// @version      0.3
// @description  Apply special effects for selected movies on Letterboxd.
// @author       none
// @match        https://letterboxd.com/film/*
// @icon         https://letterboxd.com/favicon.ico
// @grant        GM.xmlHttpRequest
// ==/UserScript==

(function() {
    'use strict';

    const GITHUB_RAW_URL = 'https://raw.githubusercontent.com/fellowjamess/movie/main/letterboxd_favorites.json';

    // Function to fetch special movies data from GitHub
    function fetchSpecialMovies(callback) {
        GM.xmlHttpRequest({
            method: 'GET',
            url: GITHUB_RAW_URL,
            onload: function(response) {
                if (response.status === 200) {
                    const specialMovies = JSON.parse(response.responseText);
                    callback(specialMovies);
                } else {
                    console.error('Failed to fetch special movies data');
                    callback([]);
                }
            },
            onerror: function() {
                console.error('Error fetching special movies data');
                callback([]);
            }
        });
    }

    // Function to apply the special effect with color based on the movie
    function applySpecialEffect(color) {
        const poster = document.querySelector(".film-poster img");
        if (poster) {
            poster.style.boxShadow = `0 0 25px ${color}`;
        }
    }

    // Function to check if filmData is available and apply the effect
    function checkAndApplyEffect(specialMovies) {
        if (typeof filmData !== 'undefined') {
            let specialMovie = specialMovies.find(movie => movie.id === filmData.id || movie.title === filmData.name);
            if (specialMovie) {
                const rgbColor = specialMovie.rgb;
                const rgbaColor = `rgba(${rgbColor[0]}, ${rgbColor[1]}, ${rgbColor[2]}, 0.75)`;
                applySpecialEffect(rgbaColor);
            }
        } else {
            console.warn("filmData is not available yet.");
        }
    }

    // Initial load and handling
    window.addEventListener('load', function() {
        fetchSpecialMovies(function(specialMovies) {
            checkAndApplyEffect(specialMovies);

            // Observe changes to the page and reapply effects if necessary
            new MutationObserver(function(mutations) {
                for (const { addedNodes } of mutations) {
                    for (const node of addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            checkAndApplyEffect(specialMovies);
                        }
                    }
                }
            }).observe(document.body, { childList: true, subtree: true });
        });
    }, false);
})();
