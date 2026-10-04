// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @notice Holds a guest USDC deposit until the settler releases or refunds it.
/// Release pays 80 percent to the operator, 10 percent to the manufacturer,
/// and 10 percent to the robot reserve. Integer dust stays with the operator.
contract ButlerEscrow {
    address public immutable usdc;
    address public immutable settler;
    address public immutable operator;
    address public immutable manufacturer;
    address public immutable reserve;

    struct Job {
        address depositor;
        uint256 amount;
        bytes32 machineId;
        bool released;
        bool refunded;
    }

    mapping(bytes32 => Job) public jobs;

    event Deposited(bytes32 indexed jobId, bytes32 indexed machineId, address indexed depositor, uint256 amount);
    event Released(
        bytes32 indexed jobId,
        uint256 operatorAmount,
        uint256 manufacturerAmount,
        uint256 reserveAmount,
        address operator,
        address manufacturer,
        address reserve
    );
    event Refunded(bytes32 indexed jobId, address indexed depositor, uint256 amount);

    error AmountZero();
    error AlreadyLocked();
    error NotSettler();
    error AlreadyDone();
    error SettlerIsOperator();
    error TransferFailed();

    constructor(
        address usdc_,
        address settler_,
        address operator_,
        address manufacturer_,
        address reserve_
    ) {
        if (settler_ == operator_) revert SettlerIsOperator();
        usdc = usdc_;
        settler = settler_;
        operator = operator_;
        manufacturer = manufacturer_;
        reserve = reserve_;
    }

    function deposit(bytes32 jobId, bytes32 machineId, uint256 amount) external {
        if (amount == 0) revert AmountZero();
        Job storage job = jobs[jobId];
        if (job.amount != 0) revert AlreadyLocked();
        if (!IERC20(usdc).transferFrom(msg.sender, address(this), amount)) revert TransferFailed();
        job.depositor = msg.sender;
        job.amount = amount;
        job.machineId = machineId;
        emit Deposited(jobId, machineId, msg.sender, amount);
    }

    function release(bytes32 jobId) external {
        if (msg.sender != settler) revert NotSettler();
        Job storage job = jobs[jobId];
        if (job.amount == 0 || job.released || job.refunded) revert AlreadyDone();
        job.released = true;

        uint256 manufacturerAmount = (job.amount * 10) / 100;
        uint256 reserveAmount = (job.amount * 10) / 100;
        uint256 operatorAmount = job.amount - manufacturerAmount - reserveAmount;

        if (!IERC20(usdc).transfer(operator, operatorAmount)) revert TransferFailed();
        if (!IERC20(usdc).transfer(manufacturer, manufacturerAmount)) revert TransferFailed();
        if (!IERC20(usdc).transfer(reserve, reserveAmount)) revert TransferFailed();

        emit Released(
            jobId, operatorAmount, manufacturerAmount, reserveAmount, operator, manufacturer, reserve
        );
    }

    function refund(bytes32 jobId) external {
        if (msg.sender != settler) revert NotSettler();
        Job storage job = jobs[jobId];
        if (job.amount == 0 || job.released || job.refunded) revert AlreadyDone();
        job.refunded = true;
        uint256 amount = job.amount;
        address depositor = job.depositor;
        if (!IERC20(usdc).transfer(depositor, amount)) revert TransferFailed();
        emit Refunded(jobId, depositor, amount);
    }
}
