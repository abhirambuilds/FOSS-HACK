import React from 'react';

const ResultCard = ({ title, score, verdict }) => {
    return (
        <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', margin: '10px 0' }}>
            <h4>{title}</h4>
            <p>Health Score: {score}</p>
            <p>Verdict: <strong>{verdict}</strong></p>
        </div>
    );
};

export default ResultCard;
