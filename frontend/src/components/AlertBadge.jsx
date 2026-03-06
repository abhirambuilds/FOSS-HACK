import React from 'react';

const AlertBadge = ({ message, type }) => {
    const color = type === 'warning' ? 'orange' : type === 'danger' ? 'red' : 'green';
    return (
        <span style={{
            backgroundColor: color,
            color: 'white',
            padding: '5px 10px',
            borderRadius: '20px',
            fontSize: '0.8em',
            marginRight: '5px'
        }}>
            {message}
        </span>
    );
};

export default AlertBadge;
