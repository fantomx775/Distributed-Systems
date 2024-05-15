package org.example;

import io.grpc.Status;
import org.example.gen.*;

import java.util.List;

public class CalculatorImpl extends CalculatorGrpc.CalculatorImplBase{

    @Override
    public void performBatchOperation(BatchOperationRequest request,
                                      io.grpc.stub.StreamObserver<BatchOperationResult> responseObserver) {
        System.out.println("Received batch operation request: " + request);

        BatchOperationResult.Builder batchResultBuilder = BatchOperationResult.newBuilder();
        for (ComplexArithmeticOpArguments operationArgs : request.getOperationsList()) {
            double result = 0.0;
            switch (operationArgs.getOptype()) {
                case SUM:
                    result = sum(operationArgs.getArgsList());
                    break;
                case AVG:
                    result = average(operationArgs.getArgsList());
                    break;
                case MIN:
                    result = min(operationArgs.getArgsList());
                    break;
                case MAX:
                    result = max(operationArgs.getArgsList());
                    break;
                default:
                    responseObserver.onError(
                            Status.INVALID_ARGUMENT
                                    .withDescription("Unsupported OperationType")
                                    .asRuntimeException());
                    return;
            }
            batchResultBuilder.addResults(ComplexArithmeticOpResult.newBuilder().setRes(result).build());
        }

        BatchOperationResult batchResult = batchResultBuilder.build();

        responseObserver.onNext(batchResult);
        responseObserver.onCompleted();
    }
    @Override
    public void add(org.example.gen.ArithmeticOpArguments request,
            io.grpc.stub.StreamObserver<org.example.gen.ArithmeticOpResult> responseObserver)
    {
        System.out.println("addRequest (" + request.getArg1() + ", " + request.getArg2() +")");
        int val = request.getArg1() + request.getArg2();
        ArithmeticOpResult result = ArithmeticOpResult.newBuilder().setRes(val).build();
        if(request.getArg1() > 100 && request.getArg2() > 100) try { Thread.sleep(5000); } catch(java.lang.InterruptedException ex) { }
        responseObserver.onNext(result);
        responseObserver.onCompleted();
    }

    @Override
    public void subtract(org.example.gen.ArithmeticOpArguments request,
            io.grpc.stub.StreamObserver<org.example.gen.ArithmeticOpResult> responseObserver)
    {
        System.out.println("subtractRequest (" + request.getArg1() + ", " + request.getArg2() +")");
        int val = request.getArg1() - request.getArg2();
        ArithmeticOpResult result = ArithmeticOpResult.newBuilder().setRes(val).build();
        responseObserver.onNext(result);
        responseObserver.onCompleted();
    }

    @Override
    public void complexOperation(ComplexArithmeticOpArguments request,
                                 io.grpc.stub.StreamObserver<ComplexArithmeticOpResult> responseObserver) {
        System.out.println("Received complex operation request: " + request);

        double result = 0.0;
        switch (request.getOptype()) {
            case SUM:
                result = sum(request.getArgsList());
                break;
            case AVG:
                result = average(request.getArgsList());
                break;
            case MIN:
                result = min(request.getArgsList());
                break;
            case MAX:
                result = max(request.getArgsList());
                break;
            default:
                responseObserver.onError(
                        Status.INVALID_ARGUMENT
                                .withDescription("Unsupported OperationType")
                                .asRuntimeException());
                return;
        }

        ComplexArithmeticOpResult response = ComplexArithmeticOpResult.newBuilder().setRes(result).build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    private double sum(List<Double> args) {
        double sum = 0.0;
        for (double arg : args) {
            sum += arg;
        }
        return sum;
    }

    private double average(List<Double> args) {
        double sum = sum(args);
        return sum / args.size();
    }

    private double min(List<Double> args) {
        return args.stream().min(Double::compareTo).orElse(0.0);
    }

    private double max(List<Double> args) {
        return args.stream().max(Double::compareTo).orElse(0.0);
    }
}
